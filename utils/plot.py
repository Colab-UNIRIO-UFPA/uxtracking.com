import io
import base64
from PIL import Image


def create_blank_image_base64():
    """
    Cria uma imagem em branco (branca) e a codifica em base64.

    Retorna:
    --------
    str
        Uma string contendo a imagem codificada em base64 no formato apropriado para uso em HTML.

    Descrição:
    ----------
    A função realiza os seguintes passos:
    1. Cria uma nova imagem em branco com dimensões 100x100 pixels e cor branca.
    2. Salva a imagem em um buffer de bytes no formato PNG.
    3. Codifica o conteúdo do buffer de bytes em base64.
    4. Retorna a string codificada em base64 no formato 'data:image/png;base64,<base64_data>'.
    """

    blank_image = Image.new(
        "RGB", (100, 100), color="white"
    )  # Cria uma imagem branca 100x100
    buffered = io.BytesIO()
    blank_image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return "data:image/png;base64," + img_base64
