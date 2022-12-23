import jieba as jieba
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time

from wordcloud import WordCloud, ImageColorGenerator
from jieba import analyse
from PIL import Image
from dependency.Pagesearch import replace_comma
from scipy.ndimage import gaussian_gradient_magnitude


# -*- coding:utf-8 -*-
def wordcloud(keyword: str):
    text = pd.read_json('tool/ETtoday_www.ettoday.net_365.txt', lines=True, orient=True,
                        encoding_errors='ignore')
    start_time = time.time()
    # keyword = input(str("input keyword here: "))

    text = pd.DataFrame(text)
    news_data = text[text.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]
    text = news_data['content'].tolist()
    data = [replace_comma(i) for i in text]
    data = ''.join(data).strip(",").replace("\n", " ")
    print(data)
    # tokenization
    jieba.set_dictionary('tool/dict.txt.big')
    jieba.analyse.set_stop_words('tool/stop_words.txt')
    tfidf_fre = analyse.extract_tags(data, topK=100, withWeight=True, allowPOS=(), withFlag=True)
    count_dic = {}
    for i in range(len(tfidf_fre)):
        count_dic[tfidf_fre[i][0]] = tfidf_fre[i][1]

    print(count_dic)
    print('drawing worldcloud.....')

    # Mask image
    # mask_color = np.array(Image.open('../tool/parrot-by-jose-mari-gimenez2.jpg'))
    # mask_color = mask_color[::3, ::3]
    # mask_image = mask_color.copy()
    # mask_image[mask_image.sum(axis=2) == 0] = 255

    # Edge detection
    # edges = np.mean([gaussian_gradient_magnitude(mask_color[:, :, i] / 255., 2) for i in range(3)], axis=0)
    # mask_image[edges > .08] = 255

    # original wordcloud
    myWordClode = WordCloud(
        width=1800,
        height=1200,
        background_color="black",
        colormap="Dark2",
        font_path='tool/SourceHanSansTW-Regular.otf'

    ).fit_words(count_dic)

    # red_bird wordcloud
    # myWordClode = WordCloud(max_words=2000,
    #                         mask=mask_image,
    #                         font_path='../tool/SourceHanSansTW-Regular.otf',
    #                         max_font_size=40,
    #                         random_state=42,
    #                         relative_scaling=0)
    #
    # myWordClode.fit_words(count_dic)

    # Create coloring from image
    # image_colors = ImageColorGenerator(mask_color)
    # myWordClode.recolor(color_func=image_colors)

    # Plot
    plt.figure(figsize=(8, 6), dpi=100)
    plt.imshow(myWordClode)
    plt.axis("off")
    print(f'process end cost ------{time.time() - start_time} seconds------ ')
    plt.show()
    # myWordClode.to_file(f'../tool/{keyword}.png')
    return count_dic, news_data

