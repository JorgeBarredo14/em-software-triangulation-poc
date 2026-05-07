FROM python:3.11-slim

WORKDIR /artefact

RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    matplotlib==3.8.4 \
    jupyter==1.0.0 \
    "pandas>=2.0" \
    "scikit-learn>=1.3" \
    "pikepdf>=8.0" \
    "pypdf>=3.0" \
 && rm -rf /root/.cache/pip

COPY . /artefact/

RUN python scripts/compute_certainty_rates.py \
 && python scripts/compute_pexcl_wilson.py \
 && python scripts/plot_matrices.py

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
