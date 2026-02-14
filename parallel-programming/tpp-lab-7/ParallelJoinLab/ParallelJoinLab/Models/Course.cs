namespace ParallelJoinLab.Models
{
    public class Course
    {
        public string Key { get; set; }           // NCHAR(4)
        public string CourseName { get; set; }    // NVARCHAR(50)
        public int Credits { get; set; }          // INTEGER
        public double Price { get; set; }         // REAL
        public int Duration { get; set; }         // INTEGER
        public bool IsOnline { get; set; }        // INTEGER (0/1)

        public Course(string key, string courseName, int credits, double price, int duration, bool isOnline)
        {
            Key = key;
            CourseName = courseName;
            Credits = credits;
            Price = price;
            Duration = duration;
            IsOnline = isOnline;
        }

        public override string ToString()
        {
            return $"{Key}: {CourseName}, Credits: {Credits}, Price: {Price:C}";
        }
    }
}