\# Smart Face-Based Attendance System



A web-based attendance management system that uses face-based matching to identify registered students and automatically record their attendance.



\## Features



\- Student registration

\- Face sample capture through camera

\- LBPH model training

\- Live face-based attendance

\- Multiple face detection

\- Automatic date and time recording

\- Prevention of duplicate attendance on the same day

\- Attendance records dashboard

\- Excel attendance export

\- Student database management

\- Web-based interface using Flask



\## Technologies Used



\- Python

\- Flask

\- OpenCV

\- OpenCV Contrib

\- NumPy

\- SQLite

\- HTML

\- CSS

\- JavaScript

\- OpenPyXL



\## Project Structure



```text

face detection project/

│

├── app.py

├── register\_student.py

├── train\_model.py

├── capture\_faces.py

├── recognize\_face.py

├── create\_database.py

├── login.py

│

├── templates/

├── static/

│

├── haarcascade\_frontalface\_default.xml

├── requirements.txt

├── README.md

└── .gitignore

```



\## How It Works



1\. Admin registers a student using Student ID and name.

2\. The system captures face samples using the camera.

3\. The collected samples are used to train the LBPH model.

4\. During attendance, the camera detects faces in real time.

5\. The system matches the detected face with registered students.

6\. If a registered student is matched, attendance is recorded with date and time.

7\. Duplicate attendance for the same student on the same day is prevented.

8\. Attendance records can be viewed from the attendance records page.

9\. Attendance data can be exported to an Excel file.



\## Application Modules



\### 1. Dashboard



The dashboard provides an overview of the attendance system, including:



\- Total registered students

\- Total attendance records

\- Today's attendance

\- Recent attendance

\- Quick access to major system functions



\### 2. Student Registration



The registration module allows the administrator to:



\- Enter Student ID

\- Enter Student Name

\- Capture face samples

\- Train the LBPH model



\### 3. Live Attendance



The attendance module uses the connected camera to:



\- Detect faces

\- Match faces with registered students

\- Display the matched student

\- Record attendance automatically

\- Prevent duplicate attendance on the same day



\### 4. Attendance Records



The records module displays:



\- Student ID

\- Student name

\- Attendance date

\- Attendance time



\### 5. Excel Export



Attendance records can be downloaded as an Excel file for further analysis and record keeping.



\## Installation



\### Step 1: Clone the Repository



```bash

git clone YOUR\_GITHUB\_REPOSITORY\_URL

```



Open the project folder:



```bash

cd face-detection-project

```



\### Step 2: Install Dependencies



Install the required Python libraries:



```bash

pip install -r requirements.txt

```



\## Run the Application



Start the Flask application:



```bash

python app.py

```



The application will run locally at:



```text

http://127.0.0.1:5000

```



Open the above address in a web browser.



\## Student Registration Workflow



1\. Open the Register Student page.

2\. Enter the Student ID.

3\. Enter the Student Name.

4\. Start the camera.

5\. Capture face samples.

6\. Train the model.

7\. Open the Mark Attendance page.

8\. Start the attendance camera.

9\. The system matches the detected face with registered student data.

10\. Attendance is automatically recorded.



\## Database



The application uses SQLite for storing:



\- Student information

\- Attendance records



The database file is excluded from the public repository because it may contain student information and attendance data.



\## Privacy



The project contains student-related data such as face samples and attendance records.



For this reason, the following generated/private files are excluded from the public GitHub repository:



```text

dataset/

trainer/

attendance/

database.db

```



These files are generated or maintained locally when the application is used.



\## Requirements



The project requires:



\- Python 3.x

\- Webcam

\- Modern web browser

\- Windows/Linux/macOS



\## Future Enhancements



\- Admin authentication and role-based access

\- Attendance filtering by date

\- Attendance analytics and charts

\- Cloud database integration

\- Email notifications

\- Mobile application

\- Improved matching under different lighting conditions

\- Student attendance percentage reports

\- Automated attendance reports



\## Limitations



\- Camera access is required for live attendance.

\- Matching accuracy can vary depending on lighting, camera quality, face angle, and available samples.

\- The current application is designed primarily for local use.

\- Student face samples and attendance data are maintained locally.



\## Project Objective



The objective of this project is to develop a simple web-based attendance management system that reduces manual attendance work and provides an automated method for recording student attendance.



\## Author



\*\*Riya Rana\*\*



B.Tech Computer Science Engineering (Data Science)



\## License



This project is developed for educational and academic purposes.

