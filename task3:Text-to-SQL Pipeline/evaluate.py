from executor import run_pipeline

def evaluate():
    # Mock benchmark dataset
    dataset = [
        {"question": "Find all customers in Boston", "expected_sql": "SELECT * FROM customers WHERE city = 'Boston';"},
        {"question": "How many orders have been shipped?", "expected_sql": "SELECT COUNT(*) FROM orders WHERE status = 'Shipped';"},
        {"question": "List the names of all employees who report to Employee Number 1002", "expected_sql": "SELECT firstName, lastName FROM employees WHERE reportsTo = 1002;"},
        # This one might trigger a failure for testing if the model misinterprets something slightly or uses a wrong column.
        {"question": "What is the total amount paid by customer 103?", "expected_sql": "SELECT SUM(amount) FROM payments WHERE customerNumber = 103;"}
    ]

    total_queries = len(dataset)
    successful = 0
    retries = 0
    failed = 0

    print(f"{'Question':<50} | {'Executed Successfully':<20} | {'Retry Needed':<15} | {'Final Status':<15}")
    print("-" * 105)

    for item in dataset:
        result = run_pipeline(item["question"])
        
        status = result["status"]
        retry = result.get("retry_needed", False)
        
        if status == "success":
            successful += 1
            if retry:
                retries += 1
        else:
            failed += 1
            
        print(f"{item['question']:<50} | {str(status == 'success'):<20} | {str(retry):<15} | {status:<15}")

    print("\n" + "=" * 50)
    print("Evaluation Complete!")
    print(f"Total Queries: {total_queries}")
    print(f"Successful Execution (Overall): {successful}/{total_queries} ({(successful/total_queries)*100:.2f}%)")
    print(f"Total Retries Needed: {retries}")
    print(f"Total Failed Queries: {failed}")
    print("=" * 50)

if __name__ == "__main__":
    evaluate()
