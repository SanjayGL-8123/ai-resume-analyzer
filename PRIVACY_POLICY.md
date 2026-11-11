gitadd # Privacy Policy for AI Resume Analyzer

**Effective Date:** August 25, 2026  
**Developer / Maintainer:** Sanjay G L  

Thank you for using **AI Resume Analyzer**. Your privacy is extremely important to us. This Privacy Policy outlines how your information is collected, used, processed, and stored when using this application.

---

## 1. Information We Collect

When you use the AI Resume Analyzer, we collect the following data provided directly by you:

* **Resume Files & Content:** Text extracted from files you upload (supported formats: PDF, DOCX, TXT), which may contain personal details such as your name, contact information, work experience, education, and skills.
* **Job Descriptions & Titles:** Text and title of the job opening you paste for analysis.
* **Analysis Output:** Generated match scores, matched skills list, and missing skills list resulting from the analysis.

---

## 2. How We Use Your Data

Your data is processed strictly for the following purposes:

* **Resume Analysis:** Vectorizing resume and job description text via TF-IDF (Term Frequency-Inverse Document Frequency) and calculating cosine similarity score.
* **Skill Gap Analysis:** Comparing resume content against a built-in skills dictionary to identify matched and missing qualifications.
* **Record Keeping:** Storing analysis history in a local MySQL database (`resumes`, `job_descriptions`, and `analysis_results` tables) to provide record tracking if database connectivity is enabled.

---

## 3. Data Storage & Security

* **Local Storage:** By default, uploaded files are stored in the local server `uploads/` directory and parsed text is stored in your configured MySQL database.
* **Third-Party Sharing:** **We do NOT share, sell, rent, or distribute your resume or personal data to any third party.**
* **Third-Party AI Services:** The core analysis is performed entirely locally on your server using Python's `scikit-learn` (TF-IDF) without transmitting text to external cloud AI APIs.

---

## 4. Your Choices & Data Retention

* **Data Deletion:** You can clear or remove stored resumes and job descriptions at any time by deleting records from the MySQL database or clearing the `uploads/` folder.
* **Offline Operation:** The application can function fully without saving records if MySQL database connectivity is turned off.

---

## 5. Contact Us

If you have any questions or concerns regarding this Privacy Policy, please contact the developer via GitHub: [@sanjayGL2006](https://github.com/sanjayGL2006).
