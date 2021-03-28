
1. Generate API from proto file (see [the reference](https://grpc.io/docs/languages/python/basics)):

```shell script
python -m grpc_tools.protoc   --mypy_out=service/codegen/   -I../protos/   --python_out=service/codegen/   --grpc_python_out=service/codegen   ../protos/feb_stats.proto ;
sed -i'' -E 's/^import.*_pb2/from . &/' service/codegen/*.py ;
```
