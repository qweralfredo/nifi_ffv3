import io
import json
import requests

MAGIC_HEADER = b"NiFiFF3"
MAX_VALUE_2_BYTES = 65535
def package_flowfile(input_stream: io.BytesIO, output_stream: io.BytesIO, attributes: dict = None, file_size: int = None):
    """
    Packages data into a flowfile-stream-v3 format.

    Args:
        input_stream (io.BytesIO): Bytes stream containing the flowfile content.
        output_stream (io.BytesIO): Bytes stream to write the packaged flowfile.
        attributes (dict, optional): Dictionary of flowfile attributes. Defaults to None.
        file_size (int, optional): Size of the flowfile content. If not provided, 
                                    it will be calculated from input_stream.
    """
    output_stream.write(MAGIC_HEADER)
    if attributes is None:
        attributes = {}

    write_field_length(output_stream, len(attributes))

    for key, value in attributes.items():
        write_string(output_stream, key)
        write_string(output_stream, value if value is not None else "")

    if file_size is None:
        file_size = len(input_stream.getvalue())

    write_long(output_stream, file_size)
    output_stream.write(input_stream.getvalue())


def write_string(output_stream: io.BytesIO, value: str):
    """Writes a string to the output stream with length prefix."""
    bytes_val = value.encode("utf-8")
    write_field_length(output_stream, len(bytes_val))
    output_stream.write(bytes_val)

def write_field_length(output_stream: io.BytesIO, num_bytes: int):
    """Writes the length of a field to the output stream."""
    if num_bytes < MAX_VALUE_2_BYTES:
        output_stream.write((num_bytes >> 8).to_bytes(1, byteorder='big'))
        output_stream.write(num_bytes.to_bytes(1, byteorder='big'))
    else:
        output_stream.write((255).to_bytes(2, byteorder='big'))  # Indicate longer length
        output_stream.write(num_bytes.to_bytes(4, byteorder='big'))

def write_long(output_stream: io.BytesIO, value: int):
    """Writes a long integer (8 bytes) to the output stream."""
    output_stream.write(value.to_bytes(8, byteorder='big'))

def send_data(data, attributes, url):
    data_str = json.dumps(data)
    input_stream = io.BytesIO(data_str.encode())
    output_stream = io.BytesIO()    
    dff = package_flowfile(input_stream, output_stream, attributes)    
    packaged_data = output_stream.getvalue()
    files = {"files": ('flowfile.bin', packaged_data, 'multipart/form-data')}    
    response = requests.post(url, files=files)
    response.raise_for_status()
    return response.text