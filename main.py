#!/usr/bin/env python3
"""
3D DTI Tractography Visualization - Main Entry Point

This pipeline loads DTI data, fits a diffusion tensor, computes Fractional Anisotropy (FA),
performs deterministic tractography, and optionally renders 3D streamlines.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv
import yaml
import numpy as np

# Add src to Python path (works both locally and in container)
sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import DataLoader
from src.tensor_fitting import TensorFitter
from src.tractography import TractographyGenerator
from src.visualization import TractVisualizer

# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Configuration loader
# -----------------------------------------------------------------------------
def load_config(config_path: str = "config.yaml") -> dict:
    """Load YAML config and override with environment variables (DTI_* prefix)."""
    if not os.path.exists(config_path):
        logger.warning(f"Config file {config_path} not found. Using defaults.")
        return {}

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Override with environment variables (prefixed with DTI_)
    for key, value in os.environ.items():
        if key.startswith("DTI_"):
            config_key = key[4:].lower()
            logger.info(f"Overriding config {config_key} with env value {value}")
            # Simple flatten override; extend for nested if needed
            config[config_key] = value

    return config


# -----------------------------------------------------------------------------
# Output directory helper
# -----------------------------------------------------------------------------
def ensure_output_dir(output_dir: str) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# Main pipeline
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="3D DTI Tractography Visualization (clinical grade)"
    )
    parser.add_argument("--config", default="config.yaml",
                        help="Path to configuration YAML file")
    parser.add_argument("--no-viz", action="store_true",
                        help="Disable 3D visualization (useful for headless servers)")
    parser.add_argument("--save-tracts", action="store_true",
                        help="Save generated streamlines to output directory as .trk file")
    args = parser.parse_args()

    # Load environment variables from .env file
    load_dotdotenv()  # fix: should be load_dotenv()
    load_dotenv()

    config = load_config(args.config)

    output_dir = config.get('OUTPUT_DIR', 'outputs')
    ensure_output_dir(output_dir)

    logger.info("=" * 50)
    logger.info("Starting DTI Tractography Pipeline")
    logger.info("=" * 50)

    # -------------------------------------------------------------------------
    # Step 1: Load DTI data
    # -------------------------------------------------------------------------
    logger.info("Step 1/4: Loading DTI data...")
    try:
        loader = DataLoader(config)
        data, gtab = loader.load()
        logger.info(f"Data shape: {data.shape}, gradients: {len(gtab.bvals)}")
    except Exception as e:
        logger.error(f"Data loading failed: {e}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # Step 2: Tensor fitting and FA computation
    # -------------------------------------------------------------------------
    logger.info("Step 2/4: Fitting diffusion tensor and computing FA...")
    try:
        fitter = TensorFitter(data, gtab)
        fa_map, tensor_fit = fitter.compute_fa()
        logger.info(f"FA range: [{fa_map.min():.3f}, {fa_map.max():.3f}]")
    except Exception as e:
        logger.error(f"Tensor fitting failed: {e}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # Step 3: Generate streamlines (tractography)
    # -------------------------------------------------------------------------
    logger.info("Step 3/4: Generating white matter streamlines...")
    try:
        tract_gen = TractographyGenerator(fa_map, tensor_fit, config)
        streamlines = tract_gen.track()
        logger.info(f"Generated {len(streamlines)} streamlines")
    except MemoryError:
        logger.error("MemoryError: reduce 'seed_count' in config (e.g., 500-1000)")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Tractography failed: {e}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # Step 4: Save and/or visualize
    # -------------------------------------------------------------------------
    if args.save_tracts:
        from dipy.io.streamline import save_trk
        trk_path = os.path.join(output_dir, "tractography.trk")
        save_trk(trk_path, streamlines, affine=np.eye(4))
        logger.info(f"Saved streamlines to {trk_path}")

    if not args.no_viz:
        logger.info("Step 4/4: Launching 3D visualization...")
        try:
            viz = TractVisualizer(streamlines, fa_map, config)
            viz.render()
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            logger.info("You can still view the saved .trk file with TrackVis.")
    else:
        logger.info("Step 4/4: Visualization disabled (--no-viz).")

    logger.info("Pipeline finished successfully.")


if __name__ == "__main__":
    main()