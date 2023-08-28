

<?php
// Connect to the MySQL database
$servername = "localhost";
$username = "root"; // Change to your MySQL username
$password = "";     // Change to your MySQL password
$dbname = "psa";

$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $number_of_cards = $_POST['number_of_cards'];
    $address = $_POST['address'];

    // Validate and sanitize input data (you should add more validation)
    $number_of_cards = intval($number_of_cards);
    $address = htmlspecialchars($address);

    // Insert the order into the database
    $sql = "INSERT INTO orders (cards, address) VALUES ('$number_of_cards', '$address')";

    if ($conn->query($sql) === TRUE) {
        echo "Order placed successfully.";
    } else {
        echo "Error: " . $sql . "<br>" . $conn->error;
    }
}

// Fetch orders data from the database
$sql = "SELECT * FROM orders";
$result = $conn->query($sql);
$orders = [];

if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $orders[] = $row;
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Order Management System</title>
    <!-- Include Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Order Management System</h1>

        <div class="row">
            <div class="col-md-6">
                <h2>Place an Order</h2>
                <form method="post" action="">
                    <div class="form-group">
                        <label for="number_of_cards">Number of Cards:</label>
                        <input type="number" class="form-control" name="number_of_cards" required>
                    </div>
                    <div class="form-group">
                        <label for="address">Address:</label>
                        <textarea class="form-control" name="address" rows="3" required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Place Order</button>
                </form>
            </div>
        </div>

        <div class="mt-4">
            <h2>Recent Orders</h2>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Order ID</th>
                        <th>Number of Cards</th>
                        <th>Address</th>
                        <th>Submission</th>
                        <th>Status</th>
                        <th>Action</th>


                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($orders as $index => $order): ?>
                        <tr>
                            <td><?= $index + 1 ?></td>
                            <td><?= $order['cards'] ?></td>
                            <td><?= $order['address'] ?></td>
                            <td><?= $order['submission'] ?></td>
                            <td><?= $order['status'] ?></td>
                            <td><a href="edit_order.php?id=<?= $order['id'] ?>" class="btn btn-info">Edit</a></td>

                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Include Bootstrap JS (optional) -->
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>

