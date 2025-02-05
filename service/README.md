
1. Generate API from proto file (see [the reference](https://grpc.io/docs/languages/python/basics)):

```shell script
python -m grpc_tools.protoc   --mypy_out=codegen/   -I../protos/   --python_out=codegen/   --grpc_python_out=codegen   ../protos/feb_stats.proto ;
sed -i'' -E 's/^import.*_pb2/from . &/' codegen/*.py ;
```
