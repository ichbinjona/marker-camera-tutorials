# Marker Camera Tutorials

This repository contains the camera database and tutorials for the Marker app.

## Structure

```
/
├── camera_database.json      # Main database file
├── assets/
│   ├── logos/               # Brand logos
│   ├── cameras/             # Camera images
│   └── tutorials/           # Tutorial screenshots
└── README.md
```

## Camera Database Format

The `camera_database.json` file contains:
- **version**: Semantic version number (increment this when making updates)
- **lastUpdated**: ISO date of last update
- **brands**: Array of camera brands
- **cameras**: Array of camera models
- **tutorials**: Array of timecode setup tutorials

### Adding a New Brand

```json
{
  "id": "brand_identifier",
  "name": "Brand Name",
  "logoUrl": "https://raw.githubusercontent.com/ichbinjona/marker-camera-tutorials/main/assets/logos/brand.png"
}
```

### Adding a New Camera

```json
{
  "id": "brand_model",
  "brandId": "brand_identifier",
  "name": "Model Name",
  "imageUrl": "https://raw.githubusercontent.com/ichbinjona/marker-camera-tutorials/main/assets/cameras/brand_model.png"
}
```

### Adding a New Tutorial

```json
{
  "id": "tutorial_identifier",
  "cameraIds": ["camera1", "camera2"],
  "title": "Tutorial Title",
  "steps": [
    {
      "id": "step1",
      "type": "text|image|imageWithText",
      "content": "Step description",
      "imageUrl": "https://...",
      "caption": "Image caption"
    }
  ]
}
```

## Tutorial Step Types

- **text**: Simple text instruction
- **image**: Just an image with optional caption
- **imageWithText**: Text instruction with accompanying image

## Updating the Database

1. Edit `camera_database.json`
2. Increment the `version` number
3. Update `lastUpdated` date
4. Commit and push changes
5. Apps will automatically fetch the update

## Assets Guidelines

### Logos
- Format: PNG with transparency
- Size: 300x300px recommended
- Naming: `brandname.png`

### Camera Images
- Format: PNG or JPG
- Size: 800x600px recommended
- Naming: `brand_model.png`

### Tutorial Screenshots
- Format: PNG or JPG
- Size: 1200px width recommended
- Naming: descriptive, e.g., `sony_fx_menu_tcub.png`
