**Windows and macOS/Linux installation instructions.**
<br>
1. Download the CyberShake Tool from this repository. 
<br>

2. Go to **https://www.python.org/downloads/** and download Python.  
When installing Python, make sure to check the boxes below. <img width="656" height="402" alt="image" src="https://github.com/user-attachments/assets/b95ef23a-ac5f-4f5e-afd6-9dd7a5cf573f" />
<br>

3. Install Dependencies/Requirements

   Run the **setup_windows.bat**. 
   This will automatically download and install all required dependencies and packages needed to run the tool.
   
   - git
   - numpy
   - pandas
   - sqlalchemy
   - mysql-connector-python
   - configparser
   - pymysql
   - matplotlib
 <br>  
 
4. Start the Tool 

    After setup is complete, run the **run_cybershake_windows.bat** file to launch the CyberShake Tool and begin using it. 
<br>

5. A built-in seismogram reader is included. Simply click on the **Read Seismogram** and the tool will display the seismogram plot.

<img width="184" height="141" alt="image" src="https://github.com/user-attachments/assets/0c0ef4f4-d83e-43ef-b0ec-b1d9cab01675" />

<br> 
<br> 

6. A built-in Large Language Model is included. Simply click on the **Ask AI** and the tool will display a window for you to ask simple questions about the CyberShake Tool.


<img width="156" height="68" alt="image" src="https://github.com/user-attachments/assets/e4d15b46-cefd-4443-8755-2dd05d0d0ff8" />
<br>
<br> 

7. A built-in Interactive Map is included. Simply click on the **Open Map** and the tool will display a map that shows all the site info and its information.
   
<img width="160" height="42" alt="image" src="https://github.com/user-attachments/assets/c4ddd4a4-ebcd-42fb-b08e-7f800629929f" />


<br>
<br>
<br>
<br>

**==== On macOS/Linux ====**  

  1.  Go to the terminal and type(assuming Python is already installed for macOS): **pip3 install numpy pandas sqlalchemy mysql-connector-python configparser** and enter. 
   Additionally, type **pip3 install pymysql**, then **pip3 install matplotlib**, and enter. Before installing requirements, make sure Python is correctly installed on your system by checking the Python version in the terminal. 
   <br>
   Type **pip3 --version** in the terminal to verify that Python is in your system. 
   <br>
   <br>
   **Image example:** 
   <br>
   <img width="718" height="34" alt="image" src="https://github.com/user-attachments/assets/f99a942b-602b-4004-b0d7-f13329faa19c" />

   <br>
   <img width="260" height="31" alt="image" src="https://github.com/user-attachments/assets/5e01fcfb-d14a-4229-a5a6-9cdb2a09e4dc" />

   <br> 
   <img width="185" height="27" alt="image" src="https://github.com/user-attachments/assets/e0ccb52b-dba9-443f-81ec-f20c3d4c49cb" />
<br> 
 <br>  

   2. Go to the terminal and type **cd ~/Downloads/cybershake-tool-master/src** and enter, then type **python3 main.py** to start the cybershake tool on macOS. <br>
   **Note**: if your file is in another location and not in "Downloads", you have to   **cd**   to the right directory in order to make the cybershake tool work. 
<br>

   3. Go to the terminal and type **cd ~/Downloads/cybershake-tool-master/src** and enter, then type **python3 seismogramsReader.py** to start the seismogram reader on macOS. <br> 
   **Note**: if your file is in another location and not in "Downloads", you have to   **cd**   to the right directory in order to make the seismogram reader work.
<br>
<br>
<br>
<br>



**MORE ABOUT THE GUI TOOL**
<br>
<br>
GUI powered by Tkinter. 
<br>

**Implementations:**
  - LLM
  - Seismogram Reader
  - Interactive Map
<br> 


**GUI Main Screen:**
<br><br>
<img width="508" height="423" alt="image" src="https://github.com/user-attachments/assets/4443b030-298e-4803-b039-15d82f443e4a" />\
<br><br>
**LLM:**
<br><br>
<img width="438" height="319" alt="image" src="https://github.com/user-attachments/assets/46b1e776-428b-43f1-a28a-9b122fd076ea" />
<br><br>
**Interactive Map:**
<br><br>
<img width="959" height="593" alt="image" src="https://github.com/user-attachments/assets/d72c79fb-0df1-49c3-a065-a8763026e76c" />
<br><br>
**Seismogram Reader:**
<br><br>
<img width="1400" height="600" alt="Figure_1" src="https://github.com/user-attachments/assets/13c9fccf-baa2-4bd5-86be-ac9c56802270" />










