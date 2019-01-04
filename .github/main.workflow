workflow "On Push" {
  on = "push"
  resolves = ["Send Email"]
}

action "Send Email" {
  uses = "./.github/send_email"
  secrets = ["SENDGRID_PASSWORD"]
}
