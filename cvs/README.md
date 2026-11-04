# cvs/

- `base_cv.docx` is **your** master CV. Put it here (Word .docx, not PDF). Every tailored CV is built from it, keeping its fonts and layout.
- `applications/<Month YYYY>/` holds every tailored CV, saved automatically. You can browse them on the app's **CV Archive** page.

Everything in this folder except this README is gitignored, so your CV never ends up on GitHub.

To change your master CV, edit `base_cv.docx` in Word, then tell Claude "I updated my base CV". It will re-check the headings still match `profile.md`.
