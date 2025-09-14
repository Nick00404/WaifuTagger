# WaifuTagger

An automated anime image tagging system powered by [SmilingWolf's WDv1-4 models](https://huggingface.co/SmilingWolf). Tags images in the Danbooru style, perfect for organizing large anime artwork collections.

## Features

- **Accurate Tagging**: Utilizes state-of-the-art WDv1-4 ConvNext models for high-accuracy tag predictions
- **Danbooru Compatibility**: Outputs tags compatible with the popular Danbooru taxonomy
- **Batch Processing**: Efficiently processes images in configurable batches
- **Tag Management**: Includes blacklisting, synonym reduction, and special rule processing
- **Memory Efficient**: Optimized for large datasets with proper garbage collection
- **Progress Tracking**: Real-time progress bars with tqdm integration

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/WaifuTagger.git
cd WaifuTagger
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

Required packages (add to requirements.txt):
```
torch>=2.0.0
transformers>=4.30.0
pillow>=9.0.0
pyyaml>=6.0
tqdm>=4.65.0
pandas>=1.5.0
psutil>=5.9.0
```

## Configuration

Edit `config.yaml` to customize the tagging process:

```yaml
model:
  id: "SmilingWolf/wd-convnext-tagger-v3"  # Model to use

paths:
  base_dir: "images"  # Root directory of your images
  output_jsonl_suffix: "data.jsonl"  # Output file suffix

folders_for_output:  # Subfolders to process
  - "01"
  - "02"
  - "03"

tagging:
  threshold: 0.35  # Confidence threshold for tags
  max_tags: 15     # Maximum number of tags per image
  blacklist_file: "blacklist.txt"  # Tags to exclude

batch_processing:
  batch_size: 4  # Images to process at once

device:
  use_cuda_if_available: true  # Use GPU if available
```

## Usage

1. **Prepare your images**: Organize them in subfolders within your base directory
2. **Configure blacklist**: Edit `blacklist.txt` to exclude unwanted tags
3. **Run the tagger**:
```bash
python app.py
```

4. **Find results**: Output JSONL files will be created in the `outputs/` directory

## Output Format

The tagger generates JSONL files with the following structure:
```json
{"image_path": "folder/subfolder/image.jpg", "tags": ["1girl", "blue_eyes", "long_hair"], "caption": ""}
{"image_path": "folder/subfolder/image2.jpg", "tags": ["2boys", "school_uniform", "fighting"], "caption": ""}
```

## Project Structure

```
WaifuTagger/
├── src/
│   ├── __init__.py
│   ├── logger.py          # Logging configuration
│   ├── selected_tags.csv  # Tag database
│   ├── tag_filtering.py   # Tag filtering logic
│   ├── tag_synonyms.py    # Synonym reduction
│   ├── tagger.py          # Main tagging class
│   └── util.py           # Utility functions
├── app.py                # Main application
├── blacklist.txt         # Blacklisted tags
├── config.yaml           # Configuration file
├── outputs/              # Generated output files
├── logs/                 # Application logs
└── README.md
```

## Customization

- **Tag Selection**: Modify `src/selected_tags.csv` to change which tags are recognized
- **Special Rules**: Edit `apply_special_rules()` in `src/tag_filtering.py` for custom tag logic
- **Synonyms**: Configure synonym groups in the config file to merge similar tags

## Performance Tips

- Use a GPU for significantly faster processing
- Adjust `batch_size` based on available VRAM/RAM
- Start with a small subset of images to test configuration
- Monitor memory usage in the logs

## Acknowledgments

- [SmilingWolf](https://huggingface.co/SmilingWolf) for the excellent WDv1-4 models
- Danbooru community for the tagging taxonomy and dataset
- Hugging Face for the Transformers library

## License

This project is available for use and modification under the MIT License.

## Support

For issues and questions, please open an issue on the GitHub repository with:
1. Your configuration file (remove sensitive paths)
2. The relevant log files
3. A description of the problem