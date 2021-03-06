import csv
import glob
import re
import sys
from flask import *
import os
app = Flask(__name__)
app.secret_key = 'secret'
@app.route('/', methods=['POST','GET'])
def main():
    if request.method == 'POST':
        folder_path = request.form.get('folderpath')
        csv_path = request.form.get('csvpath')
        # app = Flask(static_folder=folder_path)

        print('folder path ', folder_path,' csv path ', csv_path)
        if folder_path not in [None,''] and csv_path not in [None,'']:
            folder_path+='\\'
            import shutil
            for file in os.listdir(folder_path):
                source = folder_path + file
                destination = r"D:\projects\autoUploads\static"
                try:
                    shutil.copy2(source, destination)
                    # print("File copied successfully.")
                except shutil.SameFileError:
                    print("Source and destination represents the same file.")
                except IsADirectoryError:
                    print("Destination is a directory.")
                except PermissionError:
                    print("Permission denied.")
                except:
                    print("Error occurred while copying file.", sys.exc_info())
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                csvreader = csv.reader(csvfile)
                fields = next(csvreader)
                index = 0
                rows = []
                for row in csvreader:
                    rows.append(row)
                    index += 1
                batches = []
                final_list = []
                i = 0
                listoffiles = os.listdir(folder_path)
                lengthofnewlines = []
                while(i<index):

                    if rows[i][6] == 'image' and rows[i][5] in listoffiles:
                        batches.append('image')

                        image_to_appended = rows[i][5]
                        batches.append(image_to_appended)

                    elif rows[i][6] != 'video' and rows[i][6] != 'image' and batches != []:
                        batches.append('text')
                        string= ''
                        while rows[i][6] != 'image' and rows[i][6] != 'video' and i + 1 < index :
                            string = string + " " + rows[i][5]
                            i += 1
                            if rows[i][6] == 'image' or rows[i][6] == 'video':
                                i -= 1
                                break
                            print('string', string)
                        if rows[i][6] != 'image' and rows[i][6] != 'video' and i == index - 1 :
                            string = string + " " + rows[i][5]
                        sublengthofnewlines = len(re.findall(r"\\n", string))
                        string = re.sub(r"\\n", " \n ", string)
                        string = "Title : \n Description : " + string + " \nTags: \n Product_type: \n Weight: \n Price :"
                        batches.append(string)
                        # print('lengthofnewlines ', sublengthofnewlines, " ", lengthofnewlines)
                        lengthofnewlines.append(sublengthofnewlines)
                        final_list.append(batches)
                        batches = []
                    i+=1
                print('final list ', final_list)

                return render_template('index.html', final_list = final_list, folder_path=folder_path, lengthofnewlines = lengthofnewlines)
        else:
            # print("attackked   ",request.form.getlist('attack'))
            print('len of list ',len(request.form.getlist('attack')))
            print('list of check box selected ', request.form.getlist('checkboxtodelete'))
            checkboxDelete = request.form.getlist('checkboxtodelete')
            list_from_html = request.form.getlist('attack')
            temp_list = []
            final_list = []
            multi_image = []
            for i in range(0,len(list_from_html),2):
                if list_from_html[i] == 'image':
                    if list_from_html[i+1][-1] == "@":
                        list_from_html[i+1] = list_from_html[i+1][:-1]
                    for check_img in checkboxDelete:
                        if list_from_html[i+1] == check_img:
                            list_from_html[i+1]+="@D"
                    temp_list.append(list_from_html[i+1])
                elif list_from_html[i] == 'text':
                    text = list_from_html[i+1]


                    final_sub_list = []
                    j = 0
                    while(j<len(temp_list)):
                        final_sub_list_sub = []
                        try:
                            if temp_list[j].find('@') != -1:
                                print('image has @', temp_list[j])
                                batch = []
                                try:
                                    if temp_list[j].split('@')[1] == 'D' or temp_list[j].split('@')[1] == 'd':
                                        print('Delete product ', temp_list[j])
                                        final_sub_list_sub.append(temp_list[j].split('@')[0])
                                        final_sub_list_sub.append(text+" update as DPDU")
                                        final_sub_list.append(final_sub_list_sub)
                                        j+=1
                                        continue
                                    else:
                                        number = int(temp_list[j].split('@')[1].split('.')[0])
                                        index = j+1
                                        tempBatchlist = []
                                        tempBatchlist.append(temp_list[j].split('@')[0])
                                        numbers = []
                                        numbers.append(int(temp_list[j].split('@')[1].split('.')[1]))

                                        while(index<len(temp_list)):
                                            try:
                                                if temp_list[index].find('@') != -1 and temp_list[index].split('@')[1]!='D' and temp_list[index].split('@')[1]!='d':
                                                    string_to_search = temp_list[index]

                                                    splitingmainnumber = string_to_search.split('@')[1]
                                                    main_number = splitingmainnumber.split('.')[0]

                                                    num_in_string = int(main_number)
                                                    if num_in_string == number:

                                                        tempBatchlist.append(temp_list[index].split('@')[0])
                                                        numbers.append(int(splitingmainnumber.split('.')[1]))
                                                        print('temp list after remove ', temp_list)
                                                        temp_list.pop(index)
                                                        index = j
                                            except:
                                                print("This product has error !!!!!")
                                            index+=1
                                        print('temp batch list ',tempBatchlist)
                                        print('numbers ', numbers)
                                        for ij in range(0,len(numbers)):
                                            for ji in range(ij,len(numbers)):
                                                if numbers[ij]>numbers[ji]:
                                                    temp = tempBatchlist[ij]
                                                    tempBatchlist[ij] = tempBatchlist[ji]
                                                    tempBatchlist[ji] = temp
                                                    temp = numbers[ij]
                                                    numbers[ij] = numbers[ji]
                                                    numbers[ji] = temp
                                        for batching in tempBatchlist:
                                            batch.append(batching)
                                        batch.append(text+" wst")
                                        print('batches ', batch)
                                        final_sub_list.append(batch)
                                except:
                                    print("This batch has error so skipped!!!!!!!!!!")
                            else:
                                try:
                                    if text.find('@Delete') == -1 and text.find('@delete') == -1 and text.find('@DELETE') == -1:
                                        final_sub_list_sub.append(temp_list[j])
                                        final_sub_list_sub.append(text)
                                    else:
                                        final_sub_list_sub.append(temp_list[j])
                                        final_text_du = text+" update as DPDU"
                                        if final_text_du.find('@Delete') != -1:
                                            final_text_du = str(final_text_du.split('@Delete')[0]+" "+final_text_du.split('@Delete')[1])
                                        elif final_text_du.find('@delete') != -1:
                                            final_text_du = str(final_text_du.split('@delete')[0]+" "+final_text_du.split('@delete')[1])
                                        elif final_text_du.find('@DELETE') != -1:
                                            final_text_du = str(final_text_du.split('@DELETE')[0]+" "+final_text_du.split('@DELETE')[1])
                                        final_sub_list_sub.append(final_text_du)
                                except:
                                    print("Please delete this product by giving correct values ")

                                final_sub_list.append(final_sub_list_sub)
                        except:
                            print("this batch has error")
                        j+=1
                    temp_list = []
                    final_list.append(final_sub_list)
            print('final list ', final_list)
            folder_path = request.form.get('folder_path')
            seller_notes = request.form.getlist('seller_notes')
            file_name = folder_path+'updated.csv'
            title = ['Date1', 'Date2', 'Time', 'UserPhone', 'UserName', 'MessageBody', 'MediaType', 'MediaLink', 'QuotedMessage', 'QuotedMessageDate', 'QuotedMessageTime']
            with open(file_name, 'w', newline='',encoding="utf-8") as csvfile:
                # creating a csv writer object
                csvwriter = csv.writer(csvfile)

                # writing the fields
                csvwriter.writerow(title)

                # writing the data rows
                for rows in final_list:
                    for row in rows:
                        for ind in range(0, len(row)):
                            if ind != len(row)-1:

                                csvwriter.writerow(["","","","","",row[ind],"image","","","",""])
                            else:
                                row[ind] = str(row[ind].split(r"\n"))
                                # print('row ind ', row[ind][2:-2])
                                csvwriter.writerow(["","","","","",row[ind][2:-2],"","","","",""])
                dir = r'D:\projects\autoUploads\static'

                filelist = glob.glob(os.path.join(dir, "*"))
                for f in filelist:
                    os.remove(f)
    return render_template('file_path_page.html')

@app.route('/submitted/', methods=['POST','GET'])
def submmitted():
    print('coming here ')
    data = request.form.get('attack')
    print("data   ", data)
    return render_template('testing.html', image="/static/rsbc/image.jpeg")
@app.route('/test/', methods=['POST','GET'])
def test():
    # Python program to explain shutil.copyfile() method



    dir = r'F:\projects\wsmachine\autouploads\static'

    filelist = glob.glob(os.path.join(dir, "*"))
    for f in filelist:
        os.remove(f)


if __name__ == '__main__':
    app.run(debug = True, port=6565)