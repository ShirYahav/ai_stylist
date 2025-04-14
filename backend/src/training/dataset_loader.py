from datasets import load_dataset

def load_fashion_dataset():
    
    dataset = load_dataset("tomytjandra/h-and-m-fashion-caption")
    return dataset

if __name__ == "__main__":
    ds = load_fashion_dataset()
