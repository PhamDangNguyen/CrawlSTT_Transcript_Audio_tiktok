def _normalize_text(text):
    """ Chuẩn hóa từ bằng cách chuyển về viết thường và xóa bỏ dấu cách (space) dư thừa

    Args:
        text(str): Câu đầu vào
    Returns:
        (str): Câu sau khi được chuẩn hóa
    """
    text = text.lower()
    text = ' '.join(text.split())
    return text 


if __name__ == '__main__':
    text = "aaaaaAAAAAA  AAAAaaaa "
    # a = _normalize_text(text)
    print(len(text.split()))