import asyncio
import sys
from grpclib.client import Channel
from proto.engine import AlarmClusteringServiceStub, AlarmRecord


async def main(host: str = "localhost", port: int = 50051) -> None:
    async with Channel(host, port) as channel:
        stub = AlarmClusteringServiceStub(channel)

        response = await stub.analyze_online_alarm_cluster(
            request_id="test-001",
            system="TEST",
            alarm_records=[
                AlarmRecord(_source_id="A1", managed_objects="node1", probable_cause="linkDown"),
                AlarmRecord(_source_id="A2", managed_objects="node1", probable_cause="linkDown"),
                AlarmRecord(_source_id="A3", managed_objects="node2", probable_cause="cpuUsageHigh"),
            ],
        )

        print(f"status   : {response.status}")
        print(f"message  : {response.message}")
        print("results  :")
        for r in response.results:
            print(f"  {r._source_id} -> cluster={r.cluster_id}  confidence={r.confidence:.4f}")


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 50051
    asyncio.run(main(host, port))
