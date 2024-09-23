# Use the official Ubuntu image as the base
FROM ubuntu

# Install necessary packages
RUN apt-get update && apt-get install -y wget unzip python-is-python3 python3-pip

# Download Chrome with --no-check-certificate option
RUN wget --no-check-certificate https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Install Chrome
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

RUN pip install selenium pandas ipykernel matplotlib seaborn scikit-learn --break-system-packages
