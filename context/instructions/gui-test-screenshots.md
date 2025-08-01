you are tasked to test a GUI application, and you need to take screenshots of the application during the testing process, at key steps, and document the results.

# The Guidelines for Screenshot Reports

you need to create a screenshot report that looks like this, and save to 
- `<workspace_root>/tmp/screenshot-reports/<date-time>-<test-task-name>.md` for the markdown file
- `<workspace_root>/tmp/screenshot-reports/imgs` for the screenshots

```markdown
# Screenshot Report for <Application Name>

## Step 1: <Short Description of Step>

(what you are going to do in this step)

(before you do, here is a screenshot of the application)
![Screenshot 1](path/to/screenshot1.png)

(after you finished typing, here is a screenshot of the application)
![Screenshot 2](path/to/screenshot2.png)

(after you clicked the button and triggers the action, here is a screenshot of the application)
![Final Screenshot](path/to/final-screenshot.png)

## Step 2: <Short Description of Next Step>
...
(continue with the next steps in a similar format)
```
