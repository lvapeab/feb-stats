# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: feb_stats.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='feb_stats.proto',
  package='feb_stats',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x0f\x66\x65\x62_stats.proto\x12\tfeb_stats\"\'\n\x12GetFebStatsRequest\x12\x11\n\tboxscores\x18\x01 \x03(\x0c\"$\n\x13GetFebStatsResponse\x12\r\n\x05sheet\x18\x01 \x01(\x0c\x32_\n\x0f\x46\x65\x62StatsService\x12L\n\x0bGetFebStats\x12\x1d.feb_stats.GetFebStatsRequest\x1a\x1e.feb_stats.GetFebStatsResponseb\x06proto3'
)




_GETFEBSTATSREQUEST = _descriptor.Descriptor(
  name='GetFebStatsRequest',
  full_name='feb_stats.GetFebStatsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='boxscores', full_name='feb_stats.GetFebStatsRequest.boxscores', index=0,
      number=1, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=30,
  serialized_end=69,
)


_GETFEBSTATSRESPONSE = _descriptor.Descriptor(
  name='GetFebStatsResponse',
  full_name='feb_stats.GetFebStatsResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sheet', full_name='feb_stats.GetFebStatsResponse.sheet', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=71,
  serialized_end=107,
)

DESCRIPTOR.message_types_by_name['GetFebStatsRequest'] = _GETFEBSTATSREQUEST
DESCRIPTOR.message_types_by_name['GetFebStatsResponse'] = _GETFEBSTATSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GetFebStatsRequest = _reflection.GeneratedProtocolMessageType('GetFebStatsRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETFEBSTATSREQUEST,
  '__module__' : 'feb_stats_pb2'
  # @@protoc_insertion_point(class_scope:feb_stats.GetFebStatsRequest)
  })
_sym_db.RegisterMessage(GetFebStatsRequest)

GetFebStatsResponse = _reflection.GeneratedProtocolMessageType('GetFebStatsResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETFEBSTATSRESPONSE,
  '__module__' : 'feb_stats_pb2'
  # @@protoc_insertion_point(class_scope:feb_stats.GetFebStatsResponse)
  })
_sym_db.RegisterMessage(GetFebStatsResponse)



_FEBSTATSSERVICE = _descriptor.ServiceDescriptor(
  name='FebStatsService',
  full_name='feb_stats.FebStatsService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=109,
  serialized_end=204,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetFebStats',
    full_name='feb_stats.FebStatsService.GetFebStats',
    index=0,
    containing_service=None,
    input_type=_GETFEBSTATSREQUEST,
    output_type=_GETFEBSTATSRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_FEBSTATSSERVICE)

DESCRIPTOR.services_by_name['FebStatsService'] = _FEBSTATSSERVICE

# @@protoc_insertion_point(module_scope)