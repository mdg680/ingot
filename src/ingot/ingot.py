from argparse import ArgumentParser
from fastapi import FastAPI

def parse_args():
    parser = ArgumentParser(description="Ingot CLI")
    parser.add_argument("--upload", "-u", type=str, help="Upload a file")
    parser.add_argument("--download", "-d", type=str, help="Download a file")
    parser.add_argument("--list", "-l", action="store_true", help="List files")
    parser.add_argument("--delete", "-r", type=str, help="Delete a file")
    parser.add_argument("--config", "-c", type=str, help="Path to configuration file")

    return parser.parse_args()

