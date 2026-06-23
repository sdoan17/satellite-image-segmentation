# Satellite Image Semantic Segmentation Project

## Project Overview

This project implements an end-to-end semantic segmentation pipeline for satellite imagery.
The system learns pixel-level land cover classes from labeled satellite tiles.
It supports training, evaluation, model explanation, and interactive deployment.

### Objectives

- Learn pixel-to-class mapping for satellite images
- Train a reproducible semantic segmentation model
- Explain model predictions using visual attribution
- Deploy an interactive inference interface

---

## Repository Files

### 1. `segmentation.ipynb`

**Training and evaluation notebook**

Responsibilities.

- Load satellite images and segmentation masks
- Normalize inputs and encode labels
- Train a semantic segmentation model
- Track training and validation loss
- Save trained model weights

This notebook defines model behavior and performance.

---

### 2. `gradcam_satellite_segmentation.ipynb`

**Model interpretability notebook**

Responsibilities.

- Load trained segmentation weights
- Generate Grad-CAM heatmaps
- Visualize spatial attention regions
- Diagnose class confusion and failure cases

This notebook explains why predictions occur.

---

### 3. `gradio_satellite_segmentation.ipynb`

**Deployment notebook**

Responsibilities.

- Load trained model weights
- Accept user uploaded satellite images
- Run inference on demand
- Display segmentation masks in a web UI

This notebook turns the model into a usable application.

---

## Recommended Project Structure

```
project_root/
│
├── data/
│   ├── images/
│   └── masks/
│
├── models/
│   └── segmentation_model.pth
│
├── notebooks/
│   ├── segmentation.ipynb
│   ├── gradcam_satellite_segmentation.ipynb
│   └── gradio_satellite_segmentation.ipynb
│
├── requirements.txt
└── README.md
```

---

## Environment Setup

### Python Version

- Python 3.9 or newer

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r 'requirements.txt'
```

### GPU Support

- Optional
- CUDA-compatible PyTorch required for acceleration

---

## Data Preparation

### Input Format

- RGB satellite images
- Pixel-aligned segmentation masks
- Each pixel value corresponds to a class ID

### Preprocessing Requirements

- Normalize images to range 0–1
- Convert masks to 2D class label arrays
- Ensure image and mask dimensions match

### Data Validation

- No missing files
- Consistent resolution
- Reasonable class balance

---

## Training

Open `segmentation.ipynb`.

### Steps

1. Configure dataset paths
2. Set training parameters
   - Batch size
   - Learning rate
   - Epoch count
3. Run preprocessing cells
4. Train the model
5. Save trained weights to `models/`

### Outputs

- Trained segmentation model
- Training and validation loss curves
- Sample prediction visualizations

---

## Model Explanation

Open `gradcam_satellite_segmentation.ipynb`.

### Steps

1. Load trained model weights
2. Select target class
3. Generate Grad-CAM heatmaps
4. Overlay heatmaps on input images

### Use Cases

- Validate spatial attention
- Detect spurious correlations
- Improve labeling or architecture design

---

## Deployment

### Local Deployment with Gradio

Open `gradio_satellite_segmentation.ipynb`.

### Steps

1. Load trained model
2. Run the Gradio app cell
3. Open the local URL in your browser
4. Upload a satellite image
5. View segmentation output

### Deployment Options

- Local interactive demo
- Hosted notebook services
- Docker-based deployment

---

## Reproducibility

Best practices.

- Fix random seeds
- Log library versions
- Save model checkpoints
- Preserve raw datasets

---

## Limitations

- Model quality depends on label accuracy
- Small datasets increase overfitting risk
- Grad-CAM provides qualitative insight only

---

## Future Extensions

- Multi-class IoU metrics
- Larger backbone architectures
- Temporal satellite image modeling
- Cloud-based inference API
