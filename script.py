import torch
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image

def generate_image_caption(image_path):
    """
    Generates a caption for a given image using a pre-trained Transformer model.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The generated caption for the image, or an error message if caption generation fails.
    """

    # Load pretrained model, tokenizer, and feature extractor
    model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

    # Check for GPU availability and move model to GPU if possible
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Set parameters for caption generation
    max_length = 16  # Maximum length of the generated caption
    num_beams = 4  # Number of beams for beam search decoding
    gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

    try:
        # Open the image and ensure it's in RGB mode
        with Image.open(image_path) as img:
            if img.mode != "RGB":
                img = img.convert(mode="RGB")

            # Extract image features using the feature extractor
            pixel_values = feature_extractor(images=img, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(device)

            # Generate caption using the model
            with torch.no_grad():
                output_ids = model.generate(pixel_values, **gen_kwargs)

            # Decode the generated token IDs into text
            preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
            preds = [pred.strip() for pred in preds]  # Remove any leading/trailing spaces

            # Return the first generated caption or an appropriate message
            image_caption = preds[0] if preds else "No caption generated"
            return image_caption

    except FileNotFoundError:
        return f"Error: Image file '{image_path}' not found."
    except OSError as e:
        return f"Error processing image '{image_path}': {e.strerror}"
    except Exception as e:
        return f"Error processing image '{image_path}': {e}"
    finally:
        # Clean up resources if necessary (e.g., close file handles)
        pass