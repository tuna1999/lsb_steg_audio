import wave
import click

@click.group()
def cli():
	pass


@cli.command(help="Nhúng thông tin")
@click.option("--audio",type=str, required=True, help="Đường dẫn tới file âm thanh")
@click.option("--input",type=str, required=True, help="Đường dẫn tới file cần nhúng")
@click.option("--output",type=str, default="tmp.wav", help="Đường dẫn tới file kết quả")
@click.option("--passw",type=str, default="", help="Mật khẩu")
def steghide(audio, input, output, passw):
	passw = bytearray(passw.encode())
	try:
		file_data = open(input, "rb").read()
		file_data = bytearray(file_data)
	except:
		print(f"[Lỗi] {input} không tồn tại")
		return

	try:
		audio_data = wave.open(audio,mode="rb")
		# lấy giải âm thanh và chuyển nó về định dạng bytearray
		frame_bytes = bytearray(list(audio_data.readframes(audio_data.getnframes())))
	except:
		print(f"[Lỗi] {audio} không tồn tại")
		return
	
	# Mã hoá
	file_data = encrypt(file_data, passw)

	# Thêm 4 byte vào dữ liệu để biểu thị độ dài dữ liệu được nhúng
	len_data = len(file_data)
	header = len_data.to_bytes(4,byteorder='big')

	# chèn signature "tuna" để nhận biết việc nhúng tin
	file_data = b"tuna" + header + file_data

	if 8 * len(file_data) > len(frame_bytes):
		print("[Lỗi] Dữ liệu cần nhúng quá lớn")
		return

	bits = list()
	for dat in file_data:
		tmp = bin(dat)[2:].rjust(8,"0") # Căn đủ 8 bit
		for j in tmp:
			bits.append(int(j))

	# Thay đổi các bit cuối của từng frame
	for i,bit in enumerate(bits):
		frame_bytes[i] = (frame_bytes[i] & 0xFE) + bit
	
	frame_bytes_modified = bytes(frame_bytes)

	# Tạo file wav mới
	new_audio =  wave.open(output, "wb")

	new_audio.setparams(audio_data.getparams())
	new_audio.writeframes(frame_bytes_modified)

	new_audio.close()
	audio_data.close()



@cli.command(help="Trích xuất thông tin")
@click.option("--audio", required=True, help="Đường dẫn tới file âm thanh")
@click.option("--output", default="a.out", help="Đường dẫn tới file kết quả")
@click.option("--passw",default="", help="Mật khẩu")
def recovery(audio, output, passw):
	passw = bytearray(passw.encode())
	try:
		audio_data = wave.open(audio,mode="rb")
		# lấy giải âm thanh 
		frame_bytes = audio_data.readframes(audio_data.getnframes())
	except:
		print(f"[Lỗi] {audio} không tồn tại")
		return

	# Lấy các bit cuối cùng của từng frame
	bits = [frame_byte & 1 for frame_byte in frame_bytes]

	if "".join(map(str,bits[:32])) != "01110100011101010110111001100001":
		print("[Lỗi] Tập tin không có tin được nhúng")
		return
	bits = bits[32:]
	# Lấy độ dài dữ liệu được nhúng 
	len_data = int("".join(map(str,bits[:32])),2)

	# trích xuất dữ liệu
	data = bytearray()
	for i in range(32,len_data * 8 + 32,8):
		s = "".join(map(str,bits[i:i+8]))
		data.append(int(s,2))
	
	# giải mã
	data = encrypt(data, passw)

	open(output, "wb").write(data)


def encrypt(data,passw):
	if passw == b"":
		return data
	
	for i in range(len(data)):
		data[i] = data[i] ^ passw[ i % len(passw)]
	return data

if __name__ == "__main__":
	cli()