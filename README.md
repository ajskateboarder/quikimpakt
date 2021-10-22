# quikimpakt
Extract abstracts from PubMed's vast collection of scientific documents and create word meshes.

![img](https://raw.githubusercontent.com/ajskateboarder/stuff/main/site.png)
==
![img](https://raw.githubusercontent.com/ajskateboarder/stuff/main/photo.png)
==
![img](https://raw.githubusercontent.com/ajskateboarder/stuff/main/drugcloud.png)
==
![img](https://raw.githubusercontent.com/ajskateboarder/stuff/main/structure.png)

## Usage
```bash
$ git clone https://github.com/themysticsavages/quikimpakt.git
$ cd quikimpakt
$ python3 -m pip install -r requirements.txt
```
You will also need a [Photoroom](https://photoroom.com/api) API key.
```bash
$ cat .env
# Configuration
PHOTOROOMAPIKEY=https://www.photoroom.com/api/
```
When you get one and put in the dotenv file run:
```bash
$ python3 wsgi.py
```
A server instance will pop up at localhost:5000.
