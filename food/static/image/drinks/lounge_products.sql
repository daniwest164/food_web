-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Nov 16, 2025 at 03:03 PM
-- Server version: 8.4.6
-- PHP Version: 8.4.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `awjowneh_sweethome`
--

-- --------------------------------------------------------

--
-- Table structure for table `lounge_products`
--

CREATE TABLE `lounge_products` (
  `id` int NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `category` enum('food','drink') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `location` enum('Bubbles Lounge','Sweet Home Restaurant') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Bubbles Lounge',
  `product_class` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `quantity` int NOT NULL DEFAULT '0',
  `stock_limit` int NOT NULL DEFAULT '10',
  `image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('active','inactive') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `lounge_products`
--

INSERT INTO `lounge_products` (`id`, `name`, `description`, `category`, `location`, `product_class`, `price`, `quantity`, `stock_limit`, `image`, `status`, `created_at`, `updated_at`) VALUES
(9, 'Coca Cola', 'The iconic, bold taste of chilled Coca-Cola.', 'drink', 'Bubbles Lounge', NULL, 1500.00, 10000091, 30, 'uploads/products/product_1763288857_1631.jpg', 'active', '2025-09-29 11:51:28', '2025-11-16 10:27:37'),
(15, 'FULL ENGLISH BREAKFAST', 'A rich, indulgent breakfast experience built on\r\nclassic English flavors.', 'food', 'Sweet Home Restaurant', NULL, 10000.00, 10000000, 1, 'uploads/products/product_1763243492_5797.jpg', 'active', '2025-11-15 21:51:32', '2025-11-15 21:51:32'),
(16, 'YAM AND EGG SAUCE/FISH SAUCE', 'A harmonious blend of soft yam and premium sauce,\r\ncrafted for a cultured palate.', 'food', 'Sweet Home Restaurant', NULL, 9000.00, 10000000, 1, 'uploads/products/product_1763243608_2334.jpg', 'active', '2025-11-15 21:53:28', '2025-11-15 21:53:28'),
(17, 'OGI AND AKARA/MOINMOIN', 'Pure local comfort: Silky fermented ogi with akara or spiced, steamed moinmoin.', 'food', 'Sweet Home Restaurant', NULL, 6500.00, 10000000, 1, 'uploads/products/product_1763243899_8893.jpg', 'active', '2025-11-15 21:58:19', '2025-11-15 22:00:48'),
(18, 'POUNDO YAM', 'Smooth poundo yam, crafted to perfection, served with your choice of rich, flavorful soup.', 'food', 'Sweet Home Restaurant', NULL, 3000.00, 10000000, 1, 'uploads/products/product_1763244845_8983.jpg', 'active', '2025-11-15 22:14:06', '2025-11-15 22:14:06'),
(19, 'AMALA', 'Dark, silky amala offering a uniquely earthy taste, for an authentic culinary experience.', 'food', 'Sweet Home Restaurant', 'SWALLOW', 3000.00, 10000000, 1, 'uploads/products/product_1763244923_3535.jpg', 'active', '2025-11-15 22:15:23', '2025-11-16 15:01:22'),
(20, 'SEMO', 'Light, soft, and smooth semolina swallow, a perfect canvas for your preferred hearty soup.', 'food', 'Sweet Home Restaurant', NULL, 3000.00, 10000000, 1, 'uploads/products/product_1763245020_4489.jpg', 'active', '2025-11-15 22:17:00', '2025-11-15 22:17:00'),
(21, 'VEGETABLE SOUP', 'A vibrant medley of fresh leafy greens, slow-simmered with aromatic spices, creating a wholesome and nourishing bowl.', 'food', 'Sweet Home Restaurant', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763245152_2236.jpg', 'active', '2025-11-15 22:19:12', '2025-11-15 22:19:12'),
(22, 'EGUSI SOUP', 'Rich, nutty melon seed soup with seasonal vegetables, expertly spiced to create a luxurious, velvety texture.', 'food', 'Sweet Home Restaurant', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763245272_2239.jpg', 'active', '2025-11-15 22:21:12', '2025-11-15 22:21:12'),
(23, 'SEAFOOD OKRA', 'A delicate blend of seafood and okra, simmered in a subtly spiced, aromatic sauce that elevates this coastal favorite.', 'food', 'Sweet Home Restaurant', NULL, 14000.00, 10000000, 1, 'uploads/products/product_1763277301_4900.jpg', 'active', '2025-11-16 06:58:02', '2025-11-16 07:15:01'),
(24, 'VEGETABLE OKRA', 'Fresh okra and garden vegetables, lightly seasoned and simmered to create a wholesome, silky, and flavorful delicacy.', 'food', 'Sweet Home Restaurant', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763277273_8523.jpg', 'active', '2025-11-16 07:14:33', '2025-11-16 07:14:33'),
(25, 'STEW', 'A robust, slow-cooked tomato and pepper stew with a perfect balance of heat and depth.', 'food', 'Sweet Home Restaurant', NULL, 2000.00, 10000000, 1, 'uploads/products/product_1763277481_5570.jpg', 'active', '2025-11-16 07:18:01', '2025-11-16 07:18:01'),
(26, 'WHITE RICE', 'Fluffy, perfectly steamed grains, served as a pristine foundation for savory sauces and proteins.', 'food', 'Sweet Home Restaurant', NULL, 3000.00, 10000000, 1, 'uploads/products/product_1763277554_9683.jpg', 'active', '2025-11-16 07:19:14', '2025-11-16 07:19:14'),
(27, 'JOLLOF RICE', 'Aromatic, richly spiced West African classic, delicately spiced and slow-cooked to a rich, vibrant finish.', 'food', 'Sweet Home Restaurant', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763277649_3541.jpg', 'active', '2025-11-16 07:20:49', '2025-11-16 10:00:31'),
(28, 'STIRFRY SPAGHETTI', 'Al dente spaghetti with a medley of fresh vegetables and savory sauces, delivering a sophisticated twist on a continental favorite.', 'food', 'Sweet Home Restaurant', NULL, 14000.00, 10000000, 1, 'uploads/products/product_1763278402_6060.jpg', 'active', '2025-11-16 07:25:07', '2025-11-16 07:33:22'),
(29, 'CHICKEN', 'Succulent, tender chicken, expertly seasoned and grilled to golden perfection.', 'food', 'Sweet Home Restaurant', NULL, 7000.00, 10000000, 1, 'uploads/products/product_1763278202_3296.jpg', 'active', '2025-11-16 07:30:02', '2025-11-16 07:30:02'),
(30, 'CROAKER FISH', 'A whole, flaky croaker, fried until crisp, offering a delicious taste of the coast.', 'food', 'Sweet Home Restaurant', NULL, 8000.00, 10000000, 1, 'uploads/products/product_1763278316_3926.jpg', 'active', '2025-11-16 07:31:56', '2025-11-16 07:31:56'),
(31, 'PEPPER SOUP CHICKEN', 'Tender chicken simmered in a fragrant, spicy broth, igniting the senses with every spoonful.', 'food', 'Sweet Home Restaurant', NULL, 9600.00, 10000000, 1, 'uploads/products/product_1763283398_1730.jpg', 'active', '2025-11-16 08:56:38', '2025-11-16 08:56:38'),
(32, 'CROAKER FISH PEPPER SOUP', 'Fresh croaker fish cooked in a delicately spiced, broth, offering an intensely flavorful experience.', 'food', 'Sweet Home Restaurant', NULL, 16000.00, 10000000, 1, 'uploads/products/product_1763283915_2463.jpg', 'active', '2025-11-16 09:05:16', '2025-11-16 09:05:16'),
(33, 'GOATMEAT PEPPER SOUP', 'Succulent goat meat slow-cooked in a fiery, aromatic soup, creating a rich and unforgettable taste.', 'food', 'Sweet Home Restaurant', NULL, 10000.00, 10000000, 1, 'uploads/products/product_1763284615_4344.jpg', 'active', '2025-11-16 09:16:55', '2025-11-16 09:16:55'),
(34, 'CATFISH PEPPER SOUP', 'Fresh, tender catfish in a peppery, flavorful broth that celebrates the essence of Nigerian coastal cuisine.', 'food', 'Sweet Home Restaurant', 'PEPPER SOUP', 20000.00, 10000000, 1, 'uploads/products/product_1763284740_3648.jpg', 'active', '2025-11-16 09:19:00', '2025-11-16 15:02:32'),
(35, 'GRILLED CROAKER', 'A whole, premium croaker, expertly grilled with a crisp skin and succulent, flaky flesh.', 'food', 'Sweet Home Restaurant', NULL, 23000.00, 10000000, 1, 'uploads/products/product_1763285062_8201.jpg', 'active', '2025-11-16 09:24:22', '2025-11-16 09:24:22'),
(36, 'GRILLED TILAPIA', 'Perfectly grilled whole tilapia, tender and moist, infused with aromatic herbs and spices.', 'food', 'Sweet Home Restaurant', NULL, 21000.00, 10000000, 1, 'uploads/products/product_1763285162_3682.jpg', 'active', '2025-11-16 09:26:03', '2025-11-16 09:26:03'),
(37, 'GRILLED CATFISH', 'A generous, meaty catfish steak, masterfully grilled to a smoky, flavorful finish.', 'food', 'Sweet Home Restaurant', NULL, 26000.00, 10000000, 1, 'uploads/products/product_1763285313_1022.jpg', 'active', '2025-11-16 09:28:33', '2025-11-16 09:28:33'),
(38, 'GRILLED CHICKEN', 'Juicy, quarter-cut chicken, grilled to a golden char and basted with our signature seasoning.', 'food', 'Sweet Home Restaurant', NULL, 10000.00, 10000000, 1, 'uploads/products/product_1763285480_8004.jpg', 'active', '2025-11-16 09:31:20', '2025-11-16 09:31:20'),
(39, 'PLANTAIN', 'Sweet, ripe plantains, fried to a caramelized perfection; the ideal sweet-and-savory complement.', 'food', 'Sweet Home Restaurant', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763285541_3578.jpg', 'active', '2025-11-16 09:32:21', '2025-11-16 09:32:21'),
(40, 'COLESLAW', 'A crisp, creamy coleslaw, finely shredded for a refreshing crunch with every bite.', 'food', 'Sweet Home Restaurant', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763285683_1428.jpg', 'active', '2025-11-16 09:34:44', '2025-11-16 09:34:44'),
(41, 'ACTIVE JUICE', 'A vibrant and refreshing blend of fruits, packed with natural energy.', 'drink', 'Bubbles Lounge', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763286400_7352.jpg', 'active', '2025-11-16 09:46:40', '2025-11-16 09:46:40'),
(42, 'HOLLANDIA YOGHURT', 'Creamy, smooth yoghurt for a refreshing and wholesome treat.', 'drink', 'Bubbles Lounge', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763288021_1816.jpg', 'active', '2025-11-16 10:13:41', '2025-11-16 10:13:41'),
(43, 'FANTA', 'The bright, sparkling, and fruity orange classic.', 'drink', 'Bubbles Lounge', NULL, 1500.00, 10000000, 1, 'uploads/products/product_1763288145_4056.jpg', 'active', '2025-11-16 10:15:45', '2025-11-16 10:15:45'),
(44, 'SPRITE', 'Crisp, clear with the spirte feeling refreshment.', 'drink', 'Bubbles Lounge', NULL, 1500.00, 10000000, 1, 'uploads/products/product_1763288362_6670.jpg', 'active', '2025-11-16 10:19:22', '2025-11-16 10:19:22'),
(45, 'Bottled Water', 'Pure, chilled bottled water.', 'drink', 'Bubbles Lounge', NULL, 1000.00, 10000000, 1, 'uploads/products/product_1763288496_2690.jpg', 'active', '2025-11-16 10:20:40', '2025-11-16 10:21:36'),
(46, 'HEINEKEN', 'A world-renowned lager, perfectly balanced and refreshingly crisp.', 'drink', 'Bubbles Lounge', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763288942_9815.png', 'active', '2025-11-16 10:29:02', '2025-11-16 10:29:02'),
(47, 'BUDWEISER', 'The great American lager, smooth and full of character.', 'drink', 'Bubbles Lounge', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763301318_3896.jpg', 'active', '2025-11-16 10:30:16', '2025-11-16 13:55:18'),
(48, 'DESPERADOS', 'A unique and daring beer with a bold hint of tequila.', 'drink', 'Bubbles Lounge', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763289156_7066.jpg', 'active', '2025-11-16 10:32:36', '2025-11-16 10:32:36'),
(49, 'RED BULL', 'The premier energy drink that vitalizes body and mind.', 'drink', 'Bubbles Lounge', NULL, 3500.00, 10000000, 1, 'uploads/products/product_1763289245_6584.jpg', 'active', '2025-11-16 10:34:05', '2025-11-16 10:34:05'),
(50, 'BLACK BULLET', 'An intense energy shot for a powerful, instant boost.', 'drink', 'Bubbles Lounge', NULL, 4000.00, 10000000, 1, 'uploads/products/product_1763289542_7725.png', 'active', '2025-11-16 10:35:10', '2025-11-16 10:39:02'),
(51, 'HENNESSY VS', 'The benchmark for VS cognac, with a rich and robust character.', 'drink', 'Bubbles Lounge', NULL, 150000.00, 10000000, 1, 'uploads/products/product_1763289638_3556.jpg', 'active', '2025-11-16 10:40:38', '2025-11-16 10:40:38'),
(52, 'HENNESSY VSOP', 'A special order of pure Hennessy, exceptionally smooth and well-rounded.', 'drink', 'Bubbles Lounge', NULL, 190000.00, 10000000, 1, 'uploads/products/product_1763289754_4958.jpg', 'active', '2025-11-16 10:42:36', '2025-11-16 10:42:36'),
(53, 'MARTELL VS', 'A graceful cognac with vibrant fruit notes and a smooth finish.', 'drink', 'Bubbles Lounge', NULL, 140000.00, 10000000, 1, 'uploads/products/product_1763290015_5897.jpg', 'active', '2025-11-16 10:44:20', '2025-11-16 10:46:55'),
(54, 'MARTELL BLUE SWIFT', 'A bold spirit drink, Martell cognac rested in Kentucky Bourbon casks for a unique, smooth taste.', 'drink', 'Bubbles Lounge', NULL, 180000.00, 10000000, 1, 'uploads/products/product_1763290111_9479.jpg', 'active', '2025-11-16 10:48:31', '2025-11-16 10:48:31'),
(55, 'BAILEYS', 'The original Irish cream, a luxurious blend of whiskey and fresh cream.', 'drink', 'Bubbles Lounge', NULL, 60000.00, 10000000, 1, 'uploads/products/product_1763301023_3089.jpg', 'active', '2025-11-16 10:50:18', '2025-11-16 13:50:23'),
(56, 'ABSOLUT VODKA', 'A smooth, premium vodka with a rich taste and crisp finish.', 'drink', 'Bubbles Lounge', NULL, 47000.00, 10000000, 1, 'uploads/products/product_1763290362_2821.jpg', 'active', '2025-11-16 10:51:22', '2025-11-16 10:52:42'),
(57, 'SIERRA TEQUILA', 'A classic silver tequila, perfect for shots and cocktails.', 'drink', 'Bubbles Lounge', NULL, 40000.00, 10000000, 1, 'uploads/products/product_1763290786_7829.jpg', 'active', '2025-11-16 10:59:46', '2025-11-16 10:59:46'),
(58, 'OLMECA TEQUILA', 'An authentic Mexican tequila with a bold and smooth agave flavor.', 'drink', 'Bubbles Lounge', NULL, 50000.00, 10000000, 1, 'uploads/products/product_1763290921_7076.jpg', 'active', '2025-11-16 11:02:01', '2025-11-16 11:02:01'),
(59, 'TEQUILA SHOTS', 'A clean shot of premium tequila, perfect for toasting the moment.', 'drink', 'Bubbles Lounge', NULL, 4000.00, 10000000, 1, 'uploads/products/product_1763291111_3995.jpg', 'active', '2025-11-16 11:05:11', '2025-11-16 11:05:11'),
(60, 'GORDON\'S', 'The world\'s best-selling London Dry Gin, crisp and perfectly balanced.', 'drink', 'Bubbles Lounge', NULL, 30000.00, 10000000, 1, 'uploads/products/product_1763291183_4300.jpg', 'active', '2025-11-16 11:06:23', '2025-11-16 11:06:23'),
(61, 'MARTINI ROSE', 'A refreshingly sweet and fruity sparkling rosé.', 'drink', 'Bubbles Lounge', NULL, 50000.00, 10000000, 1, 'uploads/products/product_1763291290_6544.jpg', 'active', '2025-11-16 11:08:10', '2025-11-16 11:08:10'),
(62, 'ANDRE', 'A lively and fruity California sparkling wine.', 'drink', 'Bubbles Lounge', NULL, 45000.00, 10000000, 1, 'uploads/products/product_1763291353_6611.jpg', 'active', '2025-11-16 11:09:13', '2025-11-16 11:09:13'),
(63, 'LAURENT-PERRIER', 'An elegant and prestigious champagne, delicate and finely balanced.', 'drink', 'Bubbles Lounge', NULL, 210000.00, 10000000, 1, 'uploads/products/product_1763291614_1398.jpg', 'active', '2025-11-16 11:11:48', '2025-11-16 11:13:34'),
(64, 'GLENFIDDICH 12YRS', 'The world\'s most awarded single malt Scotch, uniquely fresh and fruity.', 'drink', 'Bubbles Lounge', NULL, 110000.00, 10000000, 1, 'uploads/products/product_1763292309_5890.jpg', 'active', '2025-11-16 11:25:09', '2025-11-16 11:25:09'),
(65, 'GLENFIDDICH 15YRS', 'Another most awarded single malt Scotch, uniquely fresh and fruity.', 'drink', 'Bubbles Lounge', NULL, 140000.00, 10000000, 1, 'uploads/products/product_1763292643_2994.jpg', 'active', '2025-11-16 11:30:43', '2025-11-16 11:30:43'),
(66, 'JAMESON BLACK BARREL', 'A exceptionally smooth and rich Irish whiskey with notes of butterscotch and vanilla.', 'drink', 'Bubbles Lounge', NULL, 75000.00, 10000000, 1, 'uploads/products/product_1763292861_7460.jpg', 'active', '2025-11-16 11:34:21', '2025-11-16 11:34:21'),
(67, 'JACK DANIEL\'S', 'A classic Tennessee whiskey, smooth and charcoal mellowed.', 'drink', 'Bubbles Lounge', NULL, 55000.00, 10000000, 1, 'uploads/products/product_1763292999_4145.jpg', 'active', '2025-11-16 11:36:39', '2025-11-16 11:36:39'),
(68, 'DELTA FORCE BLUE', 'A smooth and versatile blended whiskey.', 'drink', 'Bubbles Lounge', NULL, 35000.00, 10000000, 1, 'uploads/products/product_1763293164_9440.jpg', 'active', '2025-11-16 11:39:24', '2025-11-16 11:39:24'),
(69, 'CARLO ROSSI', 'A hearty and fruity jug wine, perfect for easy sharing.', 'drink', 'Bubbles Lounge', NULL, 30000.00, 10000000, 1, 'uploads/products/product_1763293455_9600.jpg', 'active', '2025-11-16 11:44:15', '2025-11-16 11:44:15'),
(70, 'FOUR COUSINS', 'A smooth, easy-drinking South African wine, delightfully fruity.', 'drink', 'Bubbles Lounge', NULL, 27000.00, 10000000, 1, 'uploads/products/product_1763293506_3566.jpg', 'active', '2025-11-16 11:45:06', '2025-11-16 11:45:06'),
(71, 'SWEET HIBISCUS', 'Tequila, passion fruit puree, hibiscus all spice, lime juice, simple syrup.', 'drink', 'Bubbles Lounge', NULL, 8000.00, 10000000, 1, 'uploads/products/product_1763299993_4558.jpg', 'active', '2025-11-16 13:33:13', '2025-11-16 13:33:13'),
(72, 'GINGER CLASSIC', 'Whiskey, passion fruit puree, fresh ginger, lime juice, simple syrup.', 'drink', 'Bubbles Lounge', NULL, 8000.00, 10000000, 1, 'uploads/products/product_1763300103_7809.jpg', 'active', '2025-11-16 13:35:04', '2025-11-16 13:35:04'),
(73, 'DAIQUIRI', 'Choice of strawberry, passion fruit, blueberry.', 'drink', 'Bubbles Lounge', NULL, 8000.00, 10000000, 1, 'uploads/products/product_1763300265_3890.jpg', 'active', '2025-11-16 13:37:45', '2025-11-16 13:37:45'),
(74, 'PORNSTAR MARTINI', 'Vodka, lime juice, simple syrup, passion fruit syrup, vanilla syrup', 'drink', 'Bubbles Lounge', NULL, 8000.00, 10000000, 1, 'uploads/products/product_1763300325_1867.jpg', 'active', '2025-11-16 13:38:45', '2025-11-16 13:38:45'),
(75, 'LONG ISLAND', 'Vodka, rum, tequila, gin, triple sec', 'drink', 'Bubbles Lounge', NULL, 10000.00, 10000000, 1, 'uploads/products/product_1763300401_1922.jpg', 'active', '2025-11-16 13:40:01', '2025-11-16 13:40:01'),
(76, 'SWEET HOME ERA', 'White rum, dark rum, angostura rum, passion fruit puree, pineapple juice.', 'drink', 'Bubbles Lounge', NULL, 10000.00, 10000000, 1, 'uploads/products/product_1763300584_3119.jpg', 'active', '2025-11-16 13:43:04', '2025-11-16 13:43:04'),
(77, 'MILKSHAKE', 'Choice of vanilla, chocolate, caramel', 'drink', 'Sweet Home Restaurant', NULL, 7000.00, 10000000, 1, 'uploads/products/product_1763300662_8691.jpg', 'active', '2025-11-16 13:44:22', '2025-11-16 13:44:22'),
(78, 'CHAPMAN', 'Orange juice, fanta, sprite, granadin', 'drink', 'Bubbles Lounge', NULL, 7000.00, 10000000, 1, 'uploads/products/product_1763301546_1004.jpg', 'active', '2025-11-16 13:46:20', '2025-11-16 13:59:06'),
(79, 'VIRGIN PORNSTAR', 'Orange juice, passion fruit puree, lime juice', 'drink', 'Bubbles Lounge', NULL, 7000.00, 10000000, 1, 'uploads/products/product_1763300867_2629.jpg', 'active', '2025-11-16 13:47:47', '2025-11-16 13:47:47');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `lounge_products`
--
ALTER TABLE `lounge_products`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_category` (`category`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_stock_check` (`quantity`,`stock_limit`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `lounge_products`
--
ALTER TABLE `lounge_products`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=80;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
