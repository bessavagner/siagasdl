# siagasdl

Baixador de dados do site siagasweb.sgb.gov.br

## Installação

1. Baixe este repositório e extraia seus arquivos (ou clone).
2. instale o pacote poetry:
```bash
pip install poetry
```
3. Na pasta do pacote, crie um ambiente de desenvolvimento do Python:

```bash
python -m venv .venv
```

3. Carrege o ambiente:

- **Linux**:

```bash
source .venv/bin/activate
```

- **Windows**:

Antes de ativar o ambiente de desenvolvimento, execute o seguinte comando:

```shell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser -Force
```

4. Então ative o ambiente:

```shell
.\.env\Scripts\Activate.ps1
```

5. E finalmente, instale o pacote `siagasdl`:

```bash
poetry install
```

## Uso

- veja Jupyter Notebook src/app.ipynb

## License

The MIT License (MIT)

Copyright (c) 2023 Vagner Bessa

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Credits

`siagasdl` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
