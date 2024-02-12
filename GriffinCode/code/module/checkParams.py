from rich.console import Console


def CheckParams(kwargs, required_params):
    console = Console()
    # required_params = ["file_name", "base_name", "save_path"]

    missing_params = []
    for param in required_params:
        if not param in kwargs:
            print(param)
            missing_params.append(param)
    # missing_params = [param for param in required_params if param not in kwargs]

    if missing_params:
        console.print(
            "[bold red]Error[/]:[bold white] Missing required parameter(s):[/]",
            ", ".join(missing_params),
            style="yellow",
        )
        console.print("\n[bold green]Usage:[/]")
        console.print("[magenta]python your_script.py[/]", end=" ")
        for param in missing_params:
            console.print(f"[blue]{param}[/]=[cyan]value[/]", end=" ")
        return False  # Indicate missing parameters

    return True  # All required parameters are present
