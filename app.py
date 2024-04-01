from predictemt import vidframe
from comment_analysis import scrapfyt
from flask import Flask, request, render_template
import os
import pytube
from matplotlib import pyplot as plt
import shutil
import io
import base64
import urllib
import hashlib
import pandas as pd
import openpyxl



app = Flask(__name__)



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')



@app.route('/predict', methods=['GET', 'POST'])
def upload():


    def plotting(temp_counts,temp_emotions):
        fig = plt.figure()  # matplotlib plot
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('equal')
        ax.pie(temp_counts, labels=temp_emotions,
               autopct='%1.2f%%')  # adding pie chart
        img = io.BytesIO()
        plt.savefig(img, format='png')  # saving piechart
        img.seek(0)
        # piechart object that can be returned to the html
        plot_data = urllib.parse.quote(base64.b64encode(img.read()).decode())
        return plot_data
    

    def ovr(weighted_score):
        if(weighted_score!="UNKNOWN"):
            if weighted_score>=0.75:
                overallresult.append("HIGHLY POSITIVE")
            elif weighted_score>0.5 and weighted_score<0.75:
                overallresult.append("POSITIVE")
            elif weighted_score==0.5:
                overallresult.append("NEUTRAL")
            elif weighted_score>0.25 and weighted_score<0.5:
                overallresult.append("NEGATIVE")
            else:
                overallresult.append("HIGHLY NEGATIVE")
        return(overallresult)


    def Total_sentiment_score(pos,neg,smileindex):
        m=max(pos,neg)
        if m==pos:
            weighted_score=(0.15*m)+(0.85*smileindex)
        else:
            weighted_score=(0.85*smileindex)-(0.15*m)
        print(weighted_score)
        return weighted_score
    

    def hashh(link):
        return hashlib.md5(link.encode()).hexdigest()
    

    if request.method == 'POST':

        if 'file' in request.files:

            f = request.files['file']
            basepath = os.path.dirname(__file__)
            print("basepath:" + basepath)
            file_path = os.path.join(basepath, 'storage', "test.mp4")
            f.save(file_path)
            overallresult=[]
            result,face=vidframe(file_path)
            try:
                smileindex=result.count('Happy')/len(result)
                smileindex=round(smileindex,2)
            except:
                smileindex="UNKNOWN"
                overallresult.append("UNKNOWN")
            print(smileindex)

            if(smileindex!="UNKNOWN"):

                if smileindex>=0.75:
                    overallresult.append("HIGHLY POSITIVE")
                elif smileindex>0.5 and smileindex<0.75:
                    overallresult.append("POSITIVE")
                elif smileindex==0.5:
                    overallresult.append("NEUTRAL")
                elif smileindex>0.25 and smileindex<0.5:
                    overallresult.append("NEGATIVE")
                else:
                    overallresult.append("HIGHLY NEGATIVE")

            print(overallresult)
            temp_emotions = ['positive', 'negative']
            positive = result.count('Happy')
            negative = (result.count('Neutral') + result.count('Disgust') + result.count('Fearful') + result.count('Sad')+result.count('Surprised'))/5
            temp_counts = [positive, negative]
            x=plotting(temp_counts,temp_emotions)
            return render_template("predict.html",smileindex=smileindex, plot_url=x,overallscore=smileindex,result=overallresult)

        else:

            df = pd.read_excel("D:/ENGINEERING/MATERIAL 8TH SEMESTER/PROJECT PHASE 2/Final Project/storage/map_table.xlsx")
            link = request.form['link']
            hash_value=hashh(link)

            if hash_value in df['Hash_value'].tolist():
                
                row=df.loc[df['Hash_value']==hash_value]
                positive=row['Video_positives'].values[0]
                negative=row['Video_negatives'].values[0]
                smileindex=row['Smile_Index'].values[0]
                pos=row['Comments_positives'].values[0]
                neg=row['Comments_negatives'].values[0]
                oss=row['Overall_sentiment_score'].values[0]
                overall_result=row['Overall_Result'].values[0]
                temp_emotions=['positive','negative']
                temp_counts=[positive,negative]
                temp_com_counts=[pos,neg]
                x=plotting(temp_counts,temp_emotions)
                y=plotting(temp_com_counts,temp_emotions)
                return render_template("predict.html",smileindex=smileindex, plot_url=x, positive=pos, negative=neg, plot_url_1=y,overallscore=oss,result=overall_result)
            
            else:

                save_path="D:/ENGINEERING/MATERIAL 8TH SEMESTER/PROJECT PHASE 2/Final Project/storage/downloads/"
                yt = pytube.YouTube(link)
                video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                video.download(save_path)
                video_file_name=video.default_filename
                video_path=os.path.join(save_path,video_file_name)
                new_file_name="test.mp4"
                new_file_path="D:/ENGINEERING/MATERIAL 8TH SEMESTER/PROJECT PHASE 2/Final Project/storage/" + new_file_name
                shutil.copyfile(video_path,new_file_path)
                overallresult=[]
                result,face=vidframe(new_file_path)
                pos,neg= scrapfyt(link)
                try:
                    smileindex=result.count('Happy')/len(result)
                    smileindex=round(smileindex,2)
                except:
                    smileindex="UNKNOWN"
                    overallresult.append("UNKNOWN")
                print(smileindex)
                pos=round(pos,2)
                neg=round(neg,2)
                ws=Total_sentiment_score(pos,neg,smileindex)
                temp_emotions = ['positive', 'negative']
                positive = result.count('Happy')
                negative = (result.count('Neutral') + result.count('Disgust') + result.count('Fearful') + result.count('Sad')+result.count('Surprised'))/5
                temp_counts = [positive, negative]
                temp_com_counts=[pos,neg]
                s_no = len(df) + 1
                video_positives = positive
                video_negatives = negative
                comments_positives = pos
                comments_negatives = neg
                overall_sentiment_score = ws
                overall_result=ovr(ws)
                new_row = pd.DataFrame({'S.No': [s_no], 
                                        'Video_link': [link],
                                        'Hash_value': [hash_value],
                                        'Video_positives': [video_positives],
                                        'Video_negatives': [video_negatives],
                                        'Smile_Index':[smileindex],
                                        'Comments_positives': [comments_positives],
                                        'Comments_negatives': [comments_negatives],
                                        'Overall_sentiment_score': [overall_sentiment_score],
                                        'Overall_Result':[overall_result]})
                df = pd.concat([df, new_row])
                df.to_excel("D:/ENGINEERING/MATERIAL 8TH SEMESTER/PROJECT PHASE 2/Final Project/storage/map_table.xlsx", index=False)
                print(f"The sentiment analysis for {link} has been added to the Excel file.")
                x=plotting(temp_counts,temp_emotions)
                y=plotting(temp_com_counts,temp_emotions)
                return render_template("predict.html",smileindex=smileindex, plot_url=x, positive=pos, negative=neg, plot_url_1=y,overallscore=ws,result=overall_result)



if __name__ == '__main__':
    app.run(debug=True)
