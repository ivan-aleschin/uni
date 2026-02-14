namespace ParallelJoinLab.Models
{
    public class Student
    {
        public string Key { get; set; }           // NCHAR(4)
        public string FirstName { get; set; }     // NVARCHAR(50)
        public string LastName { get; set; }      // NVARCHAR(50)  
        public int Age { get; set; }              // INTEGER
        public double AverageGrade { get; set; }  // REAL
        public bool IsActive { get; set; }        // INTEGER (0/1)

        public Student(string key, string firstName, string lastName, int age, double averageGrade, bool isActive)
        {
            Key = key;
            FirstName = firstName;
            LastName = lastName;
            Age = age;
            AverageGrade = averageGrade;
            IsActive = isActive;
        }

        public override string ToString()
        {
            return $"{Key}: {FirstName} {LastName}, Age: {Age}, Grade: {AverageGrade}";
        }
    }
}