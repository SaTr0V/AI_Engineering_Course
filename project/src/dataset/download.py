from datasets import load_dataset, Dataset
from dotenv import load_dotenv

from configs.config import (
    HF_TOKEN,
    DIV2K_DIR,
    FFHQ_DIR,
    DIV2K_DATASET,
    FFHQ_DATASET,
    DATA_DIR,
)


load_dotenv()

def download_and_save_div2k() -> None:
    save_path = DIV2K_DIR
    
    if save_path.exists():
        print(f"Dataset already exists at {save_path}. Skipping...")
        return

    print(f"Downloading {DIV2K_DATASET}...")
    
    # Load dataset from Hugging Face
    dataset = load_dataset(
        DIV2K_DATASET,
        token=HF_TOKEN,
        verification_mode="no_checks"
    )
    
    # Save dataset to data directory
    print(f"Saving to {save_path}...")
    dataset.save_to_disk(save_path)
    
    print(f"DIV2K done! Saved to: {save_path}")


def download_and_save_ffhq(n_images: int = 100) -> None:
    save_path = FFHQ_DIR
    
    if save_path.exists():
        print(f"Dataset already exists at {save_path}. Skipping...")
        return

    print(f"Downloading {FFHQ_DATASET}...")
    
    dataset_iterable = load_dataset(
        FFHQ_DATASET,
        split="train",
        streaming=True,
        token=HF_TOKEN
    )
    
    # We take exactly n_images from the dataset
    subset = dataset_iterable.take(n_images)
    
    dataset = Dataset.from_list(list(subset))
    
    # Save dataset to data directory
    print(f"Saving to {save_path}...")
    dataset.save_to_disk(save_path)
    
    print(f"{n_images} from FFHQ done! Saved to: {save_path}")


def main() -> None:
    print(f"Data will be saved to: {DATA_DIR}")
    download_and_save_div2k()
    download_and_save_ffhq(100)
    print("All tasks finished.")
    

if __name__ == "__main__":
    main()