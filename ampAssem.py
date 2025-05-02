import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
import os

def process_barcode(barcode, input_dir, output_dir, min_length, max_length, threads, reference, phred_quality, model):
    # Setup paths with the new output directory option
    barcode_dir = os.path.join(output_dir, barcode)
    os.makedirs(barcode_dir, exist_ok=True)
    fastq_path = os.path.join(barcode_dir, f"{barcode}.fastq")
    filtered_fastq_path = os.path.join(barcode_dir, f"{barcode}_filt.fastq")
    sorted_bam_path = os.path.join(barcode_dir, f"{barcode}.sorted.bam")
    vcf_path = os.path.join(barcode_dir, "output", "merge_output.vcf.gz")
    final_vcf_path = os.path.join(barcode_dir, f"{barcode}.final.vcf.gz")
    preconsensus_fasta_path = os.path.join(barcode_dir, f"{barcode}.preconsensus.fasta")
    final_consensus_fasta_path = os.path.join(barcode_dir, f"{barcode}.final.consensus.fasta")
    output_dir = os.path.join(barcode_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Execute processing commands
        subprocess.run(f"cat {input_dir}/{barcode}/*.fastq > {fastq_path}", shell=True, check=True)
        subprocess.run(f"fastp -i {fastq_path} -o {filtered_fastq_path} -q {phred_quality} --length_required {min_length} --length_limit {max_length}", shell=True, check=True)
        subprocess.run(f"minimap2 -ax map-ont -t {threads} {reference} {filtered_fastq_path} | samtools view -bS -F 4 | samtools sort -o {sorted_bam_path} -T reads.tmp", shell=True, check=True)
        subprocess.run(f"samtools index {sorted_bam_path}", shell=True, check=True)
        subprocess.run(f"run_clair3.sh -b {sorted_bam_path} -f {reference} -m {model} -t {threads} -p ont -o {output_dir} --haploid_precise --include_all_ctgs --no_phasing_for_fa --chunk_size=300", shell=True, check=True)
        subprocess.run(f"gunzip -c {vcf_path} > {final_vcf_path[:-3]}", shell=True, check=True)
        subprocess.run(f"bgzip -c {final_vcf_path[:-3]} > {final_vcf_path}", shell=True, check=True)
        subprocess.run(f"tabix -p vcf {final_vcf_path}", shell=True, check=True)
        subprocess.run(f"bcftools consensus -f {reference} -o {preconsensus_fasta_path} {final_vcf_path}", shell=True, check=True)
        subprocess.run(f"bedtools genomecov -bga -ibam {sorted_bam_path} -g {reference} | awk '$4 < 20' | bedtools merge > {os.path.join(barcode_dir, f'{barcode}.mask.bed')}", shell=True, check=True)
        subprocess.run(f"bedtools maskfasta -fi {preconsensus_fasta_path} -bed {os.path.join(barcode_dir, f'{barcode}.mask.bed')} -fo {final_consensus_fasta_path}", shell=True, check=True)

        print(f"Processing completed for {barcode}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {barcode}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Parallel processing of sequencing data.")
    parser.add_argument("--input_dir", required=True, help="Input directory containing FASTQ files.")
    parser.add_argument("--output_dir", required=True, help="Output directory for processed files.")
    parser.add_argument("--min_length", type=int, required=True, help="Minimum read length.")
    parser.add_argument("--max_length", type=int, required=True, help="Maximum read length.")
    parser.add_argument("--threads", type=int, required=True, help="Number of threads for parallel processing.")
    parser.add_argument("--reference", required=True, help="Reference genome FASTA file.")
    parser.add_argument("--phred_quality", type=int, required=True, help="Minimum PHRED quality for read filtering.")
    parser.add_argument("--model", required=True, help="Model for Clair3.")
    parser.add_argument("--start_barcode", type=int, required=True, help="Start of the barcode range to process.")
    parser.add_argument("--end_barcode", type=int, required=True, help="End of the barcode range to process.")
    
    args = parser.parse_args()

    # Format barcode numbers with leading zeros
    barcodes = [f"barcode{str(i).zfill(2)}" for i in range(args.start_barcode, args.end_barcode + 1)]
    with ProcessPoolExecutor(max_workers=args.threads) as executor:
        executor.map(process_barcode, barcodes, [args.input_dir]*len(barcodes), [args.output_dir]*len(barcodes), [args.min_length]*len(barcodes),
                     [args.max_length]*len(barcodes), [args.threads]*len(barcodes), [args.reference]*len(barcodes),
                     [args.phred_quality]*len(barcodes), [args.model]*len(barcodes))

if __name__ == "__main__":
    main()
import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
import os

def process_barcode(barcode, input_dir, output_dir, min_length, max_length, threads, reference, phred_quality, model):
    # Setup paths with the new output directory option
    barcode_dir = os.path.join(output_dir, barcode)
    os.makedirs(barcode_dir, exist_ok=True)
    fastq_path = os.path.join(barcode_dir, f"{barcode}.fastq")
    filtered_fastq_path = os.path.join(barcode_dir, f"{barcode}_filt.fastq")
    sorted_bam_path = os.path.join(barcode_dir, f"{barcode}.sorted.bam")
    vcf_path = os.path.join(barcode_dir, "output", "merge_output.vcf.gz")
    final_vcf_path = os.path.join(barcode_dir, f"{barcode}.final.vcf.gz")
    preconsensus_fasta_path = os.path.join(barcode_dir, f"{barcode}.preconsensus.fasta")
    final_consensus_fasta_path = os.path.join(barcode_dir, f"{barcode}.final.consensus.fasta")
    output_dir = os.path.join(barcode_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Execute processing commands
        subprocess.run(f"cat {input_dir}/{barcode}/*.fastq > {fastq_path}", shell=True, check=True)
        subprocess.run(f"fastp -i {fastq_path} -o {filtered_fastq_path} -q {phred_quality} --length_required {min_length} --length_limit {max_length}", shell=True, check=True)
        subprocess.run(f"minimap2 -ax map-ont -t {threads} {reference} {filtered_fastq_path} | samtools view -bS -F 4 | samtools sort -o {sorted_bam_path} -T reads.tmp", shell=True, check=True)
        subprocess.run(f"samtools index {sorted_bam_path}", shell=True, check=True)
        subprocess.run(f"run_clair3.sh -b {sorted_bam_path} -f {reference} -m {model} -t {threads} -p ont -o {output_dir} --haploid_precise --include_all_ctgs --no_phasing_for_fa", shell=True, check=True)
        subprocess.run(f"gunzip -c {vcf_path} > {final_vcf_path[:-3]}", shell=True, check=True)
        subprocess.run(f"bgzip -c {final_vcf_path[:-3]} > {final_vcf_path}", shell=True, check=True)
        subprocess.run(f"tabix -p vcf {final_vcf_path}", shell=True, check=True)
        subprocess.run(f"bcftools consensus -f {reference} -o {preconsensus_fasta_path} {final_vcf_path}", shell=True, check=True)
        subprocess.run(f"bedtools genomecov -bga -ibam {sorted_bam_path} -g {reference} | awk '$4 < 20' | bedtools merge > {os.path.join(barcode_dir, f'{barcode}.mask.bed')}", shell=True, check=True)
        subprocess.run(f"bedtools maskfasta -fi {preconsensus_fasta_path} -bed {os.path.join(barcode_dir, f'{barcode}.mask.bed')} -fo {final_consensus_fasta_path}", shell=True, check=True)

        print(f"Processing completed for {barcode}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {barcode}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Parallel processing of sequencing data.")
    parser.add_argument("--input_dir", required=True, help="Input directory containing FASTQ files.")
    parser.add_argument("--output_dir", required=True, help="Output directory for processed files.")
    parser.add_argument("--min_length", type=int, required=True, help="Minimum read length.")
    parser.add_argument("--max_length", type=int, required=True, help="Maximum read length.")
    parser.add_argument("--threads", type=int, required=True, help="Number of threads for parallel processing.")
    parser.add_argument("--reference", required=True, help="Reference genome FASTA file.")
    parser.add_argument("--phred_quality", type=int, required=True, help="Minimum PHRED quality for read filtering.")
    parser.add_argument("--model", required=True, help="Model for Clair3.")
    parser.add_argument("--start_barcode", type=int, required=True, help="Start of the barcode range to process.")
    parser.add_argument("--end_barcode", type=int, required=True, help="End of the barcode range to process.")
    
    args = parser.parse_args()

    # Format barcode numbers with leading zeros
    barcodes = [f"barcode{str(i).zfill(2)}" for i in range(args.start_barcode, args.end_barcode + 1)]
    with ProcessPoolExecutor(max_workers=args.threads) as executor:
        executor.map(process_barcode, barcodes, [args.input_dir]*len(barcodes), [args.output_dir]*len(barcodes), [args.min_length]*len(barcodes),
                     [args.max_length]*len(barcodes), [args.threads]*len(barcodes), [args.reference]*len(barcodes),
                     [args.phred_quality]*len(barcodes), [args.model]*len(barcodes))

if __name__ == "__main__":
    main()
import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
import os

def process_barcode(barcode, input_dir, output_dir, min_length, max_length, threads, reference, phred_quality, model):
    # Setup paths with the new output directory option
    barcode_dir = os.path.join(output_dir, barcode)
    os.makedirs(barcode_dir, exist_ok=True)
    fastq_path = os.path.join(barcode_dir, f"{barcode}.fastq")
    filtered_fastq_path = os.path.join(barcode_dir, f"{barcode}_filt.fastq")
    sorted_bam_path = os.path.join(barcode_dir, f"{barcode}.sorted.bam")
    vcf_path = os.path.join(barcode_dir, "output", "merge_output.vcf.gz")
    final_vcf_path = os.path.join(barcode_dir, f"{barcode}.final.vcf.gz")
    preconsensus_fasta_path = os.path.join(barcode_dir, f"{barcode}.preconsensus.fasta")
    final_consensus_fasta_path = os.path.join(barcode_dir, f"{barcode}.final.consensus.fasta")
    output_dir = os.path.join(barcode_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Execute processing commands
        subprocess.run(f"cat {input_dir}/{barcode}/*.fastq > {fastq_path}", shell=True, check=True)
        subprocess.run(f"fastp -i {fastq_path} -o {filtered_fastq_path} -q {phred_quality} --length_required {min_length} --length_limit {max_length}", shell=True, check=True)
        subprocess.run(f"minimap2 -ax map-ont -t {threads} {reference} {filtered_fastq_path} | samtools view -bS -F 4 | samtools sort -o {sorted_bam_path} -T reads.tmp", shell=True, check=True)
        subprocess.run(f"samtools index {sorted_bam_path}", shell=True, check=True)
        subprocess.run(f"run_clair3.sh -b {sorted_bam_path} -f {reference} -m {model} -t {threads} -p ont -o {output_dir} --haploid_precise --include_all_ctgs --no_phasing_for_fa", shell=True, check=True)
        subprocess.run(f"gunzip -c {vcf_path} > {final_vcf_path[:-3]}", shell=True, check=True)
        subprocess.run(f"bgzip -c {final_vcf_path[:-3]} > {final_vcf_path}", shell=True, check=True)
        subprocess.run(f"tabix -p vcf {final_vcf_path}", shell=True, check=True)
        subprocess.run(f"bcftools consensus -f {reference} -o {preconsensus_fasta_path} {final_vcf_path}", shell=True, check=True)
        subprocess.run(f"bedtools genomecov -bga -ibam {sorted_bam_path} -g {reference} | awk '$4 < 20' | bedtools merge > {os.path.join(barcode_dir, f'{barcode}.mask.bed')}", shell=True, check=True)
        subprocess.run(f"bedtools maskfasta -fi {preconsensus_fasta_path} -bed {os.path.join(barcode_dir, f'{barcode}.mask.bed')} -fo {final_consensus_fasta_path}", shell=True, check=True)

        print(f"Processing completed for {barcode}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {barcode}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Parallel processing of sequencing data.")
    parser.add_argument("--input_dir", required=True, help="Input directory containing FASTQ files.")
    parser.add_argument("--output_dir", required=True, help="Output directory for processed files.")
    parser.add_argument("--min_length", type=int, required=True, help="Minimum read length.")
    parser.add_argument("--max_length", type=int, required=True, help="Maximum read length.")
    parser.add_argument("--threads", type=int, required=True, help="Number of threads for parallel processing.")
    parser.add_argument("--reference", required=True, help="Reference genome FASTA file.")
    parser.add_argument("--phred_quality", type=int, required=True, help="Minimum PHRED quality for read filtering.")
    parser.add_argument("--model", required=True, help="Model for Clair3.")
    parser.add_argument("--start_barcode", type=int, required=True, help="Start of the barcode range to process.")
    parser.add_argument("--end_barcode", type=int, required=True, help="End of the barcode range to process.")
    
    args = parser.parse_args()

    # Format barcode numbers with leading zeros
    barcodes = [f"barcode{str(i).zfill(2)}" for i in range(args.start_barcode, args.end_barcode + 1)]
    with ProcessPoolExecutor(max_workers=args.threads) as executor:
        executor.map(process_barcode, barcodes, [args.input_dir]*len(barcodes), [args.output_dir]*len(barcodes), [args.min_length]*len(barcodes),
                     [args.max_length]*len(barcodes), [args.threads]*len(barcodes), [args.reference]*len(barcodes),
                     [args.phred_quality]*len(barcodes), [args.model]*len(barcodes))

if __name__ == "__main__":
    main()

