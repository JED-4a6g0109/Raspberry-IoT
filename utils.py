from sentence_transformers import SentenceTransformer, util

st_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

predefined_commands = {
    "play_sound": ["播放聲音", "播放嗽叭", "讓喇叭發聲"],
    "count_people": ["現場人數", "鏡頭中人數"]
}


def match_command(user_input):
    if not user_input:
        return None

    user_embedding = st_model.encode(user_input, convert_to_tensor=True)
    for command, examples in predefined_commands.items():
        example_embeddings = st_model.encode(examples, convert_to_tensor=True)
        similarities = util.cos_sim(user_embedding, example_embeddings)[0]
        max_similarity, max_index = similarities.max().item(), similarities.argmax().item()

        if max_similarity > 0.7:
            print(f"匹配到指令：{examples[max_index]} (相似度: {max_similarity:.2f})")
            return command

    print(f"未匹配到任何指令 (最高相似度: {max_similarity:.2f})")
    return None