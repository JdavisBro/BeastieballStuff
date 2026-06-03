import sys
import struct
import json
from io import BytesIO
from pathlib import Path

import zlib

GAME_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Beastieball")

with open("sprite_info.json") as f:
    sprite_info = json.load(f)

def get_vertex_index(vertexes, prefix: str, index: int, x: int, y: int, z: int=None):
    if x in vertexes:
        if y in vertexes[x]:
            if z is None:
                return vertexes[x][y], ""
            if z in vertexes[x][y]:
                return vertexes[x][y][z], ""
    if x not in vertexes:
        vertexes[x] = {}
    if z is None:
        vertexes[x][y] = index
    else:
        if y not in vertexes[x]:
            vertexes[x][y] = {}
        vertexes[x][y][z] = index
    return index, f"{prefix} {x} {y}{"" if z is None else f" {z}"}\n"

def transform_texcoord(x, y, sprite_transforms):
    if not sprite_transforms:
        return x, 1.0 - y
    x = (x - sprite_transforms["pageOffsetX"]) * sprite_transforms["pageScaleX"]
    x = x * sprite_transforms["spriteScaleX"] + sprite_transforms["spriteOffsetX"]
    y = (y - sprite_transforms["pageOffsetY"]) * sprite_transforms["pageScaleY"]
    y = y * sprite_transforms["spriteScaleY"] + sprite_transforms["spriteOffsetY"]
    return x, 1.0 - y

def convert_to_obj(groups: list[dict], output_fp: Path):
    output = "# OBJ file\n"
    v_i = 1
    vt_i = 1
    vn_i = 1
    v_vertexes = {}
    vt_vertexes = {}
    vn_vertexes = {}
    for group in groups:
        # output += f"o {group['name']}\n"
        # output += f"g {group['name']}\n"
        mesh_index = 0
        for mesh in group["meshes"]:
            stuff = f"{group['name']}#{mesh['texture_name']}#{mesh['texture_slot']}#{mesh['palette_slot']}#{mesh_index}#{mesh['color']}"
            output += f"o {stuff}\n"
            output += f"g {stuff}\n"
            mesh_index += 1
            sprite_transforms = None
            if mesh['texture_slot'] >= 99:
                tex_name = f"sprTex_{mesh['texture_name']}"
                if tex_name not in sprite_info: tex_name = mesh['texture_name']
                if tex_name in sprite_info: sprite_transforms = sprite_info[tex_name]
            if "vertexes" not in mesh:
                continue
            face_output = "f"
            face_count = 0
            for vertex in mesh["vertexes"]:
                x, y, z = vertex["position_3d"]
                v_index, add_str = get_vertex_index(v_vertexes, "v", v_i, x, y, z)
                if add_str:
                    output += add_str
                    v_i += 1
                # output += f"v {x} {y} {z}\n"
                vx, vy = transform_texcoord(*vertex["texcoord"], sprite_transforms)
                vt_index, add_str = get_vertex_index(vt_vertexes, "vt", vt_i, vx, vy)
                if add_str:
                    output += add_str
                    vt_i += 1
                # output += f"vt {vx} {vy}\n"
                nx, ny, nz = vertex["normal"]
                vn_index, add_str = get_vertex_index(vn_vertexes, "vn", vn_i, nx, ny, nz)
                if add_str:
                    output += add_str
                    vn_i += 1
                # output += f"vn {nx} {ny} {nz}\n"
                face_output += f" {v_index}/{vt_index}/{vn_index}"
                # vertex_i += 1
                face_count += 1
                if face_count == 3:
                    output += face_output + "\n"
                    face_output = "f"
                    face_count = 0
    with output_fp.open("w+") as f:
        f.write(output)
    # with open("out.json", "w+") as f:
    #     json.dump(groups, f)


NULL_TERM = b"\x00"

def read_string(f):
    s = b""
    while 1:
        i = f.read(1)
        if i == NULL_TERM or i == b'':
            return s.decode()
        else:
            s += i

def read_floats(f, count=1):
    return struct.unpack("f"*count, f.read(4*count))

def read_bool(f):
    return struct.unpack("?", f.read(1))[0]

def read_u8(f):
    return struct.unpack("B", f.read(1))[0]

def read_u16(f):
    return struct.unpack("H", f.read(2))[0]

def read_u32(f):
    v = f.read(4)
    return struct.unpack("I", v)[0]

def read_f32(f):
    v = f.read(4)
    return struct.unpack("f", v)[0]

def main():
    args = sys.argv[1:]

    if args:
        out = Path("out/")
        out.mkdir(exist_ok=True)
        for arg in args:
            path = Path(arg)
            convert_model(path, out / (path.stem + ".obj"))
        return

    out = Path("./models_obj/")
    out.mkdir(exist_ok=True)
    for path in (GAME_DIR / "models").glob("**/*"):
        if path.is_dir():
            continue
        output = out / path.parent.name / (path.stem + ".obj")
        output.parent.mkdir(exist_ok=True)
        print(path.stem)
        convert_model(path, output)

def convert_model(model: Path, output: Path):
    if not model.exists():
        print(f"Model Path Invalid ('{model}' not found)")
        return

    arg1 = True # always true?

    with model.open("rb") as f:
        data = f.read()
    data = zlib.decompress(data)
    print(f"{len(data)=}")
    data = BytesIO(data)

    header = read_string(data)
    if header != "dotobj @jujuadams":
        print("Not a dotobj raw file? Continuing still.")

    version = read_string(data)
    if version != "5.3.2a": # seems to be incorrect?? 5.4.2 more likely because of aabb
        print("A later version of dotobj. Might not work.")

    sha1 = read_string(data)

    mtlib = read_string(data)

    aabb_x1, aabb_y1, aabb_z1, aabb_x2, aabb_y2, aabb_z2 = read_floats(data, 6)

    size = read_u16(data)
    materials = []
    for i in range(size):
        materials.append(read_string(data))


    size = read_u16(data)
    groups = []
    print(f"Group Count: {size}")
    for i in range(size): # Groups
        group = get_group(data, arg1)
        groups.append(group)
    convert_to_obj(groups, output)
    print(header, version, sha1, mtlib, aabb_x1, aabb_y1, aabb_z1, aabb_x2, aabb_y2, aabb_z2, size, materials)

group_fields = ["surface_type", "door_type", "renders", "shadow_caster", "collider", "collider_slippery", "has_vertex_data", "windy", "rustle", "am_conditional", "matload", "shadow_receiver", "near_clip_style"]

def get_group(data, arg1):
    group = {}
    group['name'] = read_string(data)
    group['line'] = read_u32(data)
    group['meshes'] = []
    gsize = read_u16(data)
    print(group)
    for i in range(gsize):
        mesh = get_mesh(data)
        group['meshes'].append(mesh)
    if arg1:
        fieldcount = read_u16(data)
        for i in range(fieldcount):
            group[group_fields[i]] = read_u16(data)
    return group

def get_mesh(data):
    mesh = {}
    mesh['material'] = read_string(data)
    has_tangents = mesh['has_tangents'] = read_bool(data)
    mesh['primative'] = read_u8(data)
    vsize = read_u32(data)
    if vsize != 0:
        vertex_buffer = data.read(vsize)
        # vertex_buffer = mesh['buffer'] = data.read(vsize)
        mesh["vertexes"] = parse_buffer(BytesIO(vertex_buffer), has_tangents, vsize)
    mesh['palette_slot'] = read_u8(data)
    mesh['texture_slot'] = read_u8(data)
    mesh['texture_name'] = read_string(data)
    mesh['color'] = read_f32(data)
    mesh["vertex_data"] = []
    vertexdata_size = read_u32(data)
    for i in range(vertexdata_size):
        mesh["vertex_data"].append(read_f32(data))
    return mesh

BUFFER_SIZE_TYPE = {"position_3d": 12, "position": 8, "normal": 12, "colour": 4, "texcoord": 8, "texcoord2": 8, "tangent": 16}

BUFFER_FORMATS = [
    ["position_3d", "colour", "texcoord", "texcoord2", "normal"],
    ["position_3d", "colour", "texcoord", "texcoord2", "normal", "tangent"],
]

def parse_buffer(buffer: BytesIO, has_tangents: bool, size: int):
    vertexes = []
    buffer_format = BUFFER_FORMATS[int(has_tangents)]
    while buffer.tell() < size:
        vertex = {}
        for type in buffer_format:
            vertex[type] = read_buffer_format(buffer, type)
        vertexes.append(vertex)
    return vertexes

def read_buffer_format(buffer: BytesIO, format: str):
    if format == "position_3d" or format == "normal":
        return [-read_f32(buffer), read_f32(buffer), read_f32(buffer)]
    elif format == "position":
        return [read_f32(buffer), read_f32(buffer)]
    elif format == "colour" or format == "tangent":
        return read_u32(buffer)
    elif format == "texcoord" or format == "texcoord2":
        return [read_f32(buffer), read_f32(buffer)]
    return None

if __name__ == "__main__":
    main()
