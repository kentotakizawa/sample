from pydantic import BaseModel
from openai import OpenAI

class ResearchTopic(BaseModel):
    title : str
    description : str

class Topics(BaseModel):
    topics : list[ResearchTopic]

def openai_api_test(text):
    '''
    parseは，OpenAIのResponsesAPIを使用して，指定されたモデルに対して入力テキストを解析し，指定された形式で出力を取得するメソッド
    easoning={'effort':'none'}はLLMの思考プロセスを出力に含めるかどうかを制御する
    '''

    client = OpenAI(
        base_url='http://10.0.1.127:11434/v1',
        api_key='ollama',  # required, but unused
    )

    response = client.responses.parse(
        model="gemma4:e4b",
        input=text,
        text_format=Topics,
        reasoning={'effort':'none'}
    )
    return response.output_parsed

if __name__ == "__main__":
    output = openai_api_test('研究テーマに悩んでいます。何か面白いテーマはありますか？json形式で3つ提示してください。')
    print(output.topics[0].title)