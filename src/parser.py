# fitz는 PyMuPDF 라이브러리에서 가져오는 도구예요
# 마치 도서관에서 책을 읽을 수 있는 특별한 안경을 가져오는 것과 같아요!
import fitz  # PyMuPDF
# os는 운영체제와 관련된 일을 하는 도구예요. 파일이 있는지 확인하고 폴더를 만들 때 써요!
# 마치 컴퓨터의 파일 관리자 같은 거예요!
import os  # 파일과 폴더를 다루기 위한 도구예요

# def는 "함수"를 만드는 키워드예요. 함수는 요리법 같은 거예요!
# extract_text_from_pdf는 함수 이름이고, pdf_path는 이 함수가 받을 재료(매개변수)예요
# -> 이 화살표는 "이 함수가 뭘 반환하는지" 알려주는 거예요 (str은 문자열을 의미해요)
def extract_text_from_pdf(pdf_path: str) -> str:
    # os.path.exists()는 파일이 실제로 존재하는지 확인하는 거예요
    # 마치 "이 책이 책장에 있는지 확인하는" 것과 같아요!
    # not은 "아니다"라는 뜻이에요. "파일이 없다면"이라는 의미예요!
    if not os.path.exists(pdf_path):
        # raise는 "에러를 던져라"라는 뜻이에요. 마치 "문제가 있어요!"라고 외치는 것처럼!
        # FileNotFoundError는 "파일을 찾을 수 없어요"라는 특별한 에러 종류예요!
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없어요: '{pdf_path}'")
    
    # fitz.open()은 PDF 파일을 여는 거예요. 마치 책을 펼치는 것처럼!
    # doc은 열린 PDF 문서를 담는 상자예요
    doc = fitz.open(pdf_path)
    
    # text는 빈 문자열 상자예요. 여기에 나중에 텍스트를 모을 거예요
    # ""는 빈 문자열을 의미해요. 마치 빈 가방 같은 거예요!
    text = ""
    
    # for는 반복문이에요. "각각에 대해"라는 뜻이에요
    # doc 안에 있는 각 page(페이지)를 하나씩 꺼내서 반복하는 거예요
    # 마치 책의 페이지를 하나씩 넘기면서 읽는 것과 같아요!
    for page in doc:
        # page.get_text()는 그 페이지에서 텍스트를 추출하는 거예요
        # += 는 "더해서 저장해"라는 뜻이에요. 기존 text에 새로운 텍스트를 더하는 거예요
        # 마치 가방에 물건을 계속 넣는 것처럼!
        text += page.get_text()
    
    # return은 "이걸 돌려줘"라는 뜻이에요. 함수가 끝나면 text를 반환해요
    # 마치 요리를 다 만들었으니 그릇에 담아서 내놓는 것과 같아요!
    return text

# 테스트용 코드예요
# if __name__ == "__main__": 이건 "이 파일을 직접 실행했을 때만"이라는 뜻이에요
# 마치 "이 요리책을 직접 읽을 때만 이 요리를 만들어"라는 것과 같아요!
if __name__ == "__main__":
    # PDF 파일 경로를 변수에 저장해요. 나중에 쉽게 바꿀 수 있어요!
    pdf_file = "data/sample_report.pdf"
    
    # try는 "시도해봐"라는 뜻이에요. 마치 "이걸 해볼게, 혹시 문제가 생기면 잡아줘"라는 의미예요!
    try:
        # extract_text_from_pdf 함수를 호출(사용)하는 거예요
        # pdf_file 변수에 있는 경로의 PDF 파일에서 텍스트를 추출해요
        # sample_text 상자에 추출된 텍스트를 담아요
        sample_text = extract_text_from_pdf(pdf_file)
        
        # os.path.dirname()은 파일 경로에서 폴더 이름만 가져오는 거예요
        # 예: "data/sample_report.pdf" -> "data"
        # os.makedirs()는 폴더를 만드는 거예요. exist_ok=True는 "이미 있으면 괜찮아"라는 뜻이에요!
        # 마치 "책장이 없으면 만들어줘, 이미 있으면 그냥 둬"라는 의미예요!
        os.makedirs(os.path.dirname("data/sample_report.txt"), exist_ok=True)
        
        # with open()은 파일을 여는 거예요. 마치 공책을 펼치는 것처럼!
        # "w"는 "쓰기 모드"예요. 새로 쓸 수 있다는 뜻이에요
        # encoding="utf-8"은 한글도 제대로 저장할 수 있게 해주는 거예요
        # f는 파일을 가리키는 손잡이 같은 거예요
        with open("data/sample_report.txt", "w", encoding="utf-8") as f:
            # f.write()는 파일에 텍스트를 쓰는 거예요. 마치 공책에 글씨를 쓰는 것처럼!
            f.write(sample_text)
        
        # print()는 화면에 글자를 출력하는 거예요. 마치 말하는 것처럼!
        print("PDF 텍스트 추출 완료!")
    
    # except는 "만약 에러가 생기면"이라는 뜻이에요. try의 반대예요!
    # FileNotFoundError는 파일을 찾을 수 없을 때 발생하는 에러예요!
    except FileNotFoundError as e:
        # str(e)는 에러 메시지를 문자열로 바꾸는 거예요
        # print()로 친절한 메시지를 보여줘요!
        print(f"❌ 오류: {e}")
        print(f"💡 팁: '{pdf_file}' 파일이 있는지 확인해주세요!")