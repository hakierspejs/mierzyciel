FROM python
ADD ./requirements.txt .
RUN python3 -m pip install -r requirements.txt
ADD ./main.py .
ENTRYPOINT ./main.py
