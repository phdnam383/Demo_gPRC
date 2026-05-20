# Deploy & Test — Alarm Clustering Engine (gRPC)

## Yêu cầu

- Docker
- kubectl đã kết nối với cluster
- Python 3.12 + các package trong `requirements.txt` (để chạy test client)
- Namespace `ifm-mdaf` tồn tại trong cluster

---

## 1. Tạo namespace (nếu chưa có)

```bash
kubectl create namespace ifm-mdaf
```

---

## 2. Build & push Docker image

```bash
docker build -t <registry>/alarm-clustering-engine:v1.0.0 .
docker push <registry>/alarm-clustering-engine:v1.0.0
```

Thay `<registry>` bằng địa chỉ registry thực tế, ví dụ `registry.example.io`.

---

## 3. Cập nhật tên image trong deployment

Mở `k8s/deployment.yaml`, sửa dòng `image`:

```yaml
image: <registry>/alarm-clustering-engine:v1.0.0
```

---

## 4. Apply manifest lên cluster

```bash
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/deployment.yaml
```

Theo dõi rollout:

```bash
kubectl rollout status deployment/alarm-clustering-engine -n ifm-mdaf
```

Kiểm tra pod đang chạy:

```bash
kubectl get pods -n ifm-mdaf
```

Pod ở trạng thái `Running` và `READY 1/1` là thành công.

---

## 5. Xem log server

```bash
kubectl logs -n ifm-mdaf -l app=alarm-clustering-engine --tail=50
```

Server khởi động thành công khi xuất hiện dòng:

```
gRPC listening on :50051  model=/app/models
```

---

## 6. Test bằng test_client.py

### Bước 1 — Port-forward (giữ terminal này mở)

```bash
kubectl port-forward -n ifm-mdaf svc/alarm-clustering-engine 50051:50051
```

### Bước 2 — Cài dependencies (nếu chưa có)

```bash
pip install grpclib betterproto
```

### Bước 3 — Chạy test client

```bash
python test_client.py
```

Mặc định kết nối `localhost:50051`. Để chỉ định host/port khác:

```bash
python test_client.py <host> <port>
```

### Output mong đợi

```
status   : OK
message  : 2 clusters | 0 noise | 0 OOV | eps=0.xxxx | silhouette=0.xxxx
results  :
  A1 -> cluster=0  confidence=0.9xxx
  A2 -> cluster=0  confidence=0.9xxx
  A3 -> cluster=1  confidence=0.8xxx
```

| Status | Ý nghĩa |
|--------|---------|
| `OK`   | Clustering thành công |
| `WARN` | Chỉ tìm được 0 cluster (toàn noise) |
| `ERROR` | Không có alarm, hoặc toàn bộ token OOV (không có trong embeddings) |

---

## 7. Cập nhật image (khi có code mới)

```bash
docker build -t <registry>/alarm-clustering-engine:v1.0.1 .
docker push <registry>/alarm-clustering-engine:v1.0.1

kubectl set image deployment/alarm-clustering-engine \
  alarm-clustering-engine=<registry>/alarm-clustering-engine:v1.0.1 \
  -n ifm-mdaf

kubectl rollout status deployment/alarm-clustering-engine -n ifm-mdaf
```

---

## 8. Gỡ lỗi thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|-----|-------------|------------|
| `ImagePullBackOff` | Image không tồn tại hoặc chưa push | Kiểm tra tên image và registry |
| `CrashLoopBackOff` | Server crash khi khởi động | Xem log với `kubectl logs` |
| `Internal Server Error` | Exception trong handler | Xem log server để lấy stack trace |
| `Connection refused` | Port-forward chưa chạy hoặc pod chưa ready | Kiểm tra pod status và chạy lại port-forward |
| `ERROR: All N alarms are OOV` | Token không có trong `embeddings.npz` | Kiểm tra `managed_objects` và `probable_cause` gửi lên |
