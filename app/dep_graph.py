import networkx as nx
import asyncio
import os

graphs = dict()

async def generate_graph(file: str, token: str):
    global graphs

    proc = await asyncio.create_subprocess_shell(
        f'pip-compile {file} -o {file}.out --strip-extras',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    try:
        with open(f'{file}.out', "r") as out:
            G = nx.DiGraph()
            root = 'Your project'
            G.add_node(root)
            package = None
            for line in out.readlines():
                line = line.strip()
                if len(line) == 0 or line[0] == '#' and not package:
                    continue
                if line[0] != '#':
                    package, version = line.split('==')
                    G.add_node(package, version=f'=={version}')
                else:
                    line = line.lstrip(' ')
                    if line.startswith('# via'):
                        line = line[len('# via'):]
                    line = line.lstrip('# ')
                    if len(line) == 0:
                        continue
                    if line[0] == '-': # root package
                        G.add_edge(root, package)
                    else:
                        G.add_edge(line, package)
            graphs[token] = (G, None)
            print('Graph was written correctly')
            os.remove(f'{file}.out')
    except FileNotFoundError:
        graphs[token] = (None, stderr.decode().split('\n')[0])
    os.remove(f'{file}')
