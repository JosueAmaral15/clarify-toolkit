const [expandedItems, setExpandedItems] = useState([]);
const filteredFAQs = data.filter(item => item.active);
const faqCategories = ["General", "Technical", "Billing"];
