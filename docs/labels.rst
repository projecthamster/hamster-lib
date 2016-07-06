Labels and Milestones
======================
Each issue should have at least one label from the Type and Status
section assigned.

Type (#cc317c)
---------------
Enhancement
   Issues that introduce new functionality. Original post should include the
   following information:

   * Description of desired functionality
   * A (prosaic) description of a use case
   * Optionally add suggestions/ideas about how to implement the feature. As
     always, PRs are welcome. :)

Bug
   Issues about something not working as intended. Original post should include
   the following information:

   * Platform (operating system, architecture)
   * Version of package in question
   * Steps suitable to reproduce the problem
   * Error message/console output
   * If you are willing to share: log files

   In case of an error within the documentation the above requirements can be
   omitted.

Duplicate
   Indicates that the issues topic has been addressed before and
   all discussion/comments should happen in the referenced issue instead.

Question
   Indicates that the issue is less about actual code/functionality but
   addresses a general (design) question that needs to be decided upon before
   an implementation can be considered.

Story
   Used to track multiple related issues.

Topic (#fbca04)
------------------
Issues without a specific topic assigned deal with general functionality.
The main purpose if these labels is to allow contributors with specific
skill sets to find issues fitting them.

UX
   Issue does not deal with functionality itself but with user interaction.

UI
   Issue deal with visual representation of functionality.

Documentation
   Issue does not require actual coding or even necessarily python
   knowledge at all but deals with documenting the project itself. It may be
   used to indicate improvements to the code's documentation, in which case a
   basic familiarity with the language and code layout is highly desirable.
   However, it may also be used for issues dealing with front end user facing
   documentation that elaborates on how to use the package in a plain natural
   language.

Packaging
   Issues related to project package releases.

Meta
   Issues related to the general project setup.


Status (#159818)
-----------------
Labels that indicate the status of an issue. Their provide a quick and easy
answer to whether the issue is actionable or not.

Decision needed
   Tickets that need a design decision are blocked for development until a
   project leader clarifies the way in which the issue should be approached.

Information needed
   This label indicates that the issue has not enough information in order to
   decide on how to go forward. See the documentation about our triage process
   for more information.

Help needed
   Designates issues which seem to require a certain skill currently not
   available to the core developers. Such issues are unlikely to be solved
   unless a contributor with the required skill-set steps forward to help out.
   Giving pointers to domain specific resources or best practices may already
   be enough. This does not necessarily imply that all the actual coding has to
   be done by the person providing the desired skill.

Ready
   The issue has been screened by the core devs and may be worked upon at your
   leisure.

Blocked
  This issue can only be addressed once another issue has been resolved. The
  cause may be an internal issue or external dependency.

In progress:
   Issues currently worked on. If you want to join work on it please coordinate
   with its assignee to achieve the best possible solution and avoid duplicate
   work.

Rejected:
   Issues that are not considered within the general goals of the project.
   A reference to said previous discussion/issue should be given.

Other
---------------
Labels that did not warrant their own group.

Ready for review
    Pull Requests that are considered complete. A review by at least one core
    developer is required prior to merging it.

Good First Bug
   This label marks tickets that are easy to get started with. The ticket
   should be ideal for beginners to dive into the code base, indicating
   `low-hanging fruits <http://www.urbandictionary.com/define.php?term=low-hanging%20fruit>`_.
   These tickets generally should fit the following requirements:

   * No comprehensive knowledge of the entire code base needed.
   * No particular 3rd party library familiarity required.
   * Most likely does not involve long term effort.
   * No elaborate design decisions involved.


