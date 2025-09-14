import cv2
import json
from ultralytics import YOLO
from shapely.geometry import Point, Polygon

# -----------------------------
# CONFIGURATION
# -----------------------------
VIDEO_PATH = "yolo_drone_output.avi"
OUTPUT_JSON = "traffic_summary_final.json"
INTERVAL = 5        # seconds per interval
RESIZE_TO = (640, 360)  # for YOLO processing speed

# Lane polygons (1920x1080 reference)
LANES = {
    "S_W_b": [(0, 133), (428, 373),(381,396),(0,180)],
    "E_3": [(0,83),(490,340),(430,373),(0,133)],
    "E_2": [(0,34),(552,310),(496,344),(0,83)],
    "E_1": [(24,0),(610,284),(550,313),(0,34)],
    "N_W": [(129,0),(685,252),(640,273),(24,0)],
    "W_3": [(280,0),(781,216),(720,242),(194,0)],
    "W_2": [(372,0),(832,193),(781,216),(280,0)],
    "W_1": [(449,0),(885,193),(832,193),(372,0)],
    "S_b": [(0,892),(392,533),(418,558),(0,954)],
    "S_1": [(0,954),(418,558),(506,620),(85,1077)],
    "W_S": [(124,1078),(552,660),(604,702),(261,1078)],
    "N_1": [(261,1078),(602,701),(665,754),(396,1077)],
    "E_S": [(396,1077),(665,754),(741,816),(524,1077)],
    "E_b": [(1152,849),(1426,1078),(1326,1076),(1113,885)],
    "E_6": [(1225,774),(1712,1078),(1560,1076),(1158,832)],
    "E_5": [(1294,701),(1914,1062),(1712,1078),(1225,774)],
    "E_4": [(1345,649),(1916,953),(1914,1058),(1294,701)],
    "S_E": [(1429,568),(1917,804),(1918,885),(1396,608)],
    "W_5": [(1501,514),(1918,709),(1917,778),(1456,553)],
    "W_4": [(1533,480),(1918,653),(1918,709),(1501,514)],
    "N_E": [(1565,444),(1917,593),(1918,653),(1533,480)],
    "W_N_b": [(1134,167),(1604,137),(1614,157),(1169,185)],
    "S_2": [(1169,185),(1614,157),(1672,197),(1237,212)],
    "E_N": [(1237,212),(1655,168),(1677,197),(1292,235)],
    "N_2": [(1337,257),(1677,197),(1771,247),(1452,305)]
}

# Intersection polygons
INTERSECTIONS = {
    "Junction_1": [(1070,130),(1621,375),(1405,594),(668,262)],
    "Junction_2": [(668,262),(1405,594),(981,992),(304,450)]
}

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def scale_polygons(polygons, orig_w, orig_h, new_w, new_h):
    scale_x = new_w / orig_w
    scale_y = new_h / orig_h
    scaled = {}
    for name, pts in polygons.items():
        scaled[name] = [(int(x * scale_x), int(y * scale_y)) for (x, y) in pts]
    return scaled

def sec_to_hms(total_sec):
    h = int(total_sec // 3600)
    m = int((total_sec % 3600) // 60)
    s = int(total_sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def get_interval_timestamp(seconds, interval=INTERVAL):
    start = int(seconds // interval) * interval
    end = start + interval
    return f"{sec_to_hms(start)} - {sec_to_hms(end)}"

# -----------------------------
# MAIN ANALYZER
# -----------------------------
def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open video: {video_path}")
        return

    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"[INFO] FPS: {fps:.2f}, Frames: {total_frames}, Size: {orig_w}x{orig_h}")

    new_w, new_h = RESIZE_TO

    # Scale lanes + intersections
    all_polygons = {**LANES, **INTERSECTIONS}
    scaled_polys = scale_polygons(all_polygons, orig_w, orig_h, new_w, new_h)
    poly_shapes = {name: Polygon(pts).buffer(2) for name, pts in scaled_polys.items()}

    # Load YOLO model
    model = YOLO("yolov8n.pt")

    results_summary = {}
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_resized = cv2.resize(frame, (new_w, new_h))
        current_time_sec = frame_count / fps
        timestamp = get_interval_timestamp(current_time_sec)

        if timestamp not in results_summary:
            results_summary[timestamp] = {"vehicle_counts": {}, "vehicle_departures": []}

        # YOLO detection
        try:
            results = model.predict(frame_resized, verbose=False, imgsz=new_w, device=0, half=True)
        except Exception as e:
            print(f"[WARNING] YOLO failed at frame {frame_count}: {e}")
            frame_count += 1
            continue

        for r in results:
            for box in r.boxes:
                try:
                    cls = int(box.cls[0])
                    label = model.names[cls]
                    if label not in ["car", "bus", "truck"]:
                        continue

                    x1, y1, x2, y2 = box.xyxy[0]
                    cx, cy = int((x1+x2)/2), int((y1+y2)/2)
                    point = Point(cx, cy)

                    lane_name = "unknown"
                    for name, poly in poly_shapes.items():
                        if poly.contains(point):
                            lane_name = name
                            break

                    # update counts
                    results_summary[timestamp]["vehicle_counts"].setdefault(label, 0)
                    results_summary[timestamp]["vehicle_counts"][label] += 1

                    vehicle_id = f"{label}_{frame_count}"
                    results_summary[timestamp]["vehicle_departures"].append({
                        "vehicle_id": vehicle_id,
                        "type": label,
                        "lane": lane_name,
                        "depart": round(current_time_sec, 2)
                    })

                except Exception as e:
                    print(f"[WARNING] Box error frame {frame_count}: {e}")

        frame_count += 1

    cap.release()

    # save JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results_summary, f, indent=4)

    print(f"[INFO] Analysis complete. Saved to {OUTPUT_JSON}")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    analyze_video(VIDEO_PATH)
