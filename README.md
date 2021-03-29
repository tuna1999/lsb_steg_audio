
```
pip3 install click
```

```powershell
PS D:\Code\Steg> py -3 .\main.py --help
Usage: main.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.     

Commands:
  recovery  Trích xuất thông tin
  steghide  Nhúng thông tin
```

```powershell
PS D:\Code\Steg> py -3 .\main.py steghide --audio=sample.wav --input=sample.txt --output=res.wav --passw=123456
PS D:\Code\Steg> py -3 .\main.py recovery --audio=res.wav --output=res.txt --passw=123456
```
