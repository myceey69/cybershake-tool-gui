1. Download the CyberShake Tool from this repository. 
<br>
<br>

2. Go to **https://www.python.org/downloads/** and download Python.  
When installing Python, make sure to check the boxes below. (on Windows) <img width="656" height="402" alt="image" src="https://github.com/user-attachments/assets/b95ef23a-ac5f-4f5e-afd6-9dd7a5cf573f" />
<br>
<br>

3. Install Dependencies/Requirements

   Run the **setup_windows.bat**. 
   This will automatically download and install all required dependencies and packages needed to run the tool. (only on Windows)
   
   - git
   - numpy
   - pandas
   - sqlalchemy
   - mysql-connector-python
   - configparser
   - pymysql
   - matplotlib
  
**==== On macOS, you have to download and install the files manually. ====**  

   Go to the terminal and type(assuming Python is already installed for macOS): **pip3 install numpy pandas sqlalchemy mysql-connector-python configparser** and enter. 
   Additionally, type **pip3 install pymysql**, then **pip3 install matplotlib**, and enter. 
   <br>
   <br>
   Before installing requirements, make sure Python is correctly installed on your system by checking the Python version in the terminal. 
   <br>
   Type **pip3 --version** in the terminal to verify that Python is in your system. 
   <br>
   <br>
   **Image example:** 
   <br>
   <img width="576" height="38" alt="image" src="https://github.com/user-attachments/assets/76f1766c-9a08-4c03-8f77-4edde201d8b4" />
   <br>
   <img width="167" height="26" alt="image" src="https://github.com/user-attachments/assets/729460b1-4d9c-4e48-a06e-0ff88da1ea53" />
   <br> 
   <img width="195" height="40" alt="image" src="https://github.com/user-attachments/assets/f7271693-bcdb-4ac8-8b21-3075ed5201ef" />




 <br>  
 <br>  
 
4. Start the Tool 

    After setup is complete, run the **run_cybershake_windows.bat** file to launch the CyberShake Tool and begin using it. (only on Windows)

**==== On macOS, you have to manually go through the terminal to run the code. ====**

   Go to the terminal and type **cd ~/Downloads/cybershake-tool-master/src** and enter, then type **python3 main.py** to start the cybershake tool on macOS. <br>
   **Note**: if your file is in another location and not in "Downloads", you have to   **cd**   to the right directory in order to make the cybershake tool work. 

<br>
<br>
5. A built-in seismogram reader is included. Simply run seismogram_reader.bat, then copy the filename of the seismogram file retrieved in the output folder, paste it when prompted, and the tool will display the seismogram plot. (only on Windows)


<img width="938" height="510" alt="image" src="https://github.com/user-attachments/assets/be7c2738-0708-429a-b0c7-6bbbbe500089" />


**==== On macOS, you have  to manually go through the terminal to run the code. ====**

   Go to the terminal and type **cd ~/Downloads/cybershake-tool-master/src** and enter, then type **python3 seismogramsReader.py** to start the seismogram reader on macOS. <br> 
   **Note**: if your file is in another location and not in "Downloads", you have to   **cd**   to the right directory in order to make the seismogram reader work.
<br>
<br>
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










