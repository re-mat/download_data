import json
import os

import typer
from rich import print_json
from rich.console import Console
from rich.table import Table

from pyclowder.client import ClowderClient
from pyclowder.datasets import DatasetsApi

with open("clowder_key.txt", "r") as f:
    key = f.read().strip()

clowder = ClowderClient(
    host="https://re-mat.clowder.ncsa.illinois.edu/",
    key=key)

console = Console()

app = typer.Typer()
spaces_app = typer.Typer()
datasets_app = typer.Typer()

app.add_typer(spaces_app, name="spaces")
app.add_typer(datasets_app, name="datasets")

@spaces_app.command("list")
def spaces():
    spaces_dict = clowder.get("/spaces")
    table = Table(title="Clowder Spaces")
    table.add_column("Name", style="cyan")
    table.add_column("ID", style="magenta")
    table.add_column("datasets", style="green")

    for space in spaces_dict:
        datasets = clowder.get(f"/spaces/{space['id']}/datasets")
        table.add_row(space['name'], space['id'], str(len(datasets)))

    console.print(table)

@spaces_app.command("download")
def download_space(space_id: str):
    datasets = clowder.get(f"/spaces/{space_id}/datasets")
    for dataset_rec in datasets:
        if os.path.isdir(dataset_rec['id']):
            console.print(f"Dataset {dataset_rec['id']} already downloaded")
        else:
            console.print(f"Downloading dataset {dataset_rec['id']}")
            download_dataset(dataset_rec['id'])

    print_json(data=datasets[0])


@datasets_app.command("list")
def list_datasets(space: str):
    """
    List all datasets in a specific space.
    """
    datasets = clowder.get(f"/spaces/{space}/datasets")  # Assuming this endpoint exists

    table = Table(title=f"Datasets in Space: {space}")
    table.add_column("Name", style="cyan")
    table.add_column("ID", style="magenta")

    for dataset in datasets:
        table.add_row(
            dataset.get('name', 'N/A'),
            dataset.get('id', 'N/A'),
        )

    console.print(table)

@datasets_app.command("download")
def download_dataset(dataset_id: str):
    os.mkdir(dataset_id)
    metadata = clowder.get(f"/datasets/{dataset_id}/metadata.jsonld")
    with open(f"{dataset_id}/metadata.jsonld", "w") as f:
        json.dump(metadata, f, indent=4)

    dsc_file = [file for file in clowder.get(f"/datasets/{dataset_id}/files")
                if file['filename']=='DSC_Curve.csv']
    clowder.get_file(f"/files/{dsc_file[0]['id']}", os.path.join(dataset_id, "DSC_Curve.csv"))

if __name__ == "__main__":
    app()
