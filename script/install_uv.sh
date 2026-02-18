#!/usr/bin/env bash

set -e  # exit on error

echo "Activating your virtualenv if not already (assuming you're in it)"
# If not activated yet: source .venv/bin/activate

echo "Installing the necessary packages from requirements.txt ..."
uv pip install -r script/requirements.txt

echo "Installing pytorch3d from git (stable branch) ..."
# If you need a specific version/tag, change @stable to @v0.7.8 or similar
uv pip install "git+https://github.com/facebookresearch/pytorch3d.git@stable"

# Alternative: if git install fails due to build deps, try a prebuilt wheel if available for your torch/cuda
# (check https://dl.fbaipublicfiles.com/pytorch3d/packaging/wheels/ for your py/torch/cuda combo)
# Example:
# uv pip install --no-index --no-cache-dir pytorch3d -f https://dl.fbaipublicfiles.com/pytorch3d/packaging/wheels/py310_cu121_pyt20/download.html

echo "Adjusting code in sapien/wrapper/urdf_loader.py ..."
# Find sapien location (should be in your venv's site-packages)
SAPIEN_LOCATION=$(uv pip show sapien | grep 'Location' | awk '{print $2}')/sapien
if [ -z "$SAPIEN_LOCATION" ]; then
  echo "ERROR: sapien not found. Install it first with: uv pip install sapien"
  exit 1
fi

URDF_LOADER="$SAPIEN_LOCATION/wrapper/urdf_loader.py"

if [ ! -f "$URDF_LOADER" ]; then
  echo "ERROR: urdf_loader.py not found at $URDF_LOADER"
  exit 1
fi

# Apply patch: add encoding="utf-8"
sed -i -E 's/("r")(\))( as)/\1, encoding="utf-8")\3/g' "$URDF_LOADER"
echo "Patched $URDF_LOADER"

echo "Adjusting code in mplib/planner.py ..."
MPLIB_LOCATION=$(uv pip show mplib | grep 'Location' | awk '{print $2}')/mplib
if [ -z "$MPLIB_LOCATION" ]; then
  echo "ERROR: mplib not found. Install it first with: uv pip install mplib"
  exit 1
fi

PLANNER="$MPLIB_LOCATION/planner.py"

if [ ! -f "$PLANNER" ]; then
  echo "ERROR: planner.py not found at $PLANNER"
  exit 1
fi

# Apply patch: remove "or collide"
sed -i -E 's/(if np.linalg.norm\(delta_twist\) < 1e-4 )(or collide )(or not within_joint_limit:)/\1\3/g' "$PLANNER"
echo "Patched $PLANNER"

echo "Installing Curobo ..."
cd envs || { echo "ERROR: envs/ folder not found"; exit 1; }

if [ -d "curobo" ]; then
  echo "curobo already exists → pulling latest"
  cd curobo
  git pull
else
  git clone https://github.com/NVlabs/curobo.git
  cd curobo
fi

# Install editable, no isolation (important for curobo's build)
uv pip install -e . --no-build-isolation

cd ../..  # back to root

echo "Installation basic environment complete!"
echo -e "You need to:"
echo -e "    1. \033[34m\033[1m(Important!)\033[0m Download assets from huggingface (objects.zip etc.)."
echo -e "    2. Install requirements for running baselines. (Optional)"
echo "See INSTALLATION.md for more instructions."
echo ""
echo "If errors during pytorch3d or curobo build → ensure torch matches CUDA version and build deps (gcc, cmake) are installed."