from fastapi import FastAPI, Request, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pygments import highlight
from pyvis.network import Network
import networkx as nx
import os

import dep_graph
import uuid

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def generate_graph_html(G: nx.DiGraph) -> str:
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#000000", directed=True)
    highlight_node = 'Your project'
    for node, attributes in G.nodes(data=True):
        color = "#FFC0CB" if node == highlight_node else "#97c2fc"
        size = 25 if node == highlight_node else 10
        net.add_node(
            node,
            label=node,
            title=f"{attributes.get('version', 'N/A')}",
            value=attributes.get('value', 1),
            color=color,
            size=size
        )

    for edge in G.edges():
        net.add_edge(edge[0], edge[1], color="#005f99", width=1)

    return net.generate_html()

@app.get("/", response_class=HTMLResponse)
async def main(request: Request, message: str = None):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Dependency Visualizer", "message": message}
    )


@app.get("/graph/{token}")
async def show_graph(request: Request, token: str):
    if token in dep_graph.graphs:
        G, stderr = dep_graph.graphs[token]
        if G is not None:
            graph_html = await generate_graph_html(G)
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "graph_html": graph_html}
            )
        else:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "title": "Dependency Visualizer", "error_message": f'{stderr}'}
            )
    else:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "title": "Dependency Visualizer",
             "message": "Graph is being generated. Please keep refreshing page..."}
        )


@app.post("/upload/")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    token = uuid.uuid4().hex
    file_path = os.path.join(UPLOAD_DIR, token)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        background_tasks.add_task(dep_graph.generate_graph, file_path, token)

        return RedirectResponse(url=f'/graph/{token}', status_code=303)
    except:
        return RedirectResponse(url=f'/', status_code=303)
