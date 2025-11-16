# main.tf
# Esto es solo un ejemplo para que Checkov tenga qué escanear.

terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

# Definición (ficticia) de la llave SSH
resource "digitalocean_ssh_key" "centinela_key" {
  name       = "centinela_deploy_key"
  public_key = "ssh-rsa AAAAB3Nza... (tu llave pública iría aquí)"
}

# Definición (ficticia) del Servidor VPS
resource "digitalocean_droplet" "centinela_vps" {
  image  = "ubuntu-22-04-x64"
  name   = "servidor-centinela"
  region = "nyc3"
  size   = "s-1vcpu-1gb"
  ssh_keys = [
    digitalocean_ssh_key.centinela_key.id
  ]

  # ¡Un error de seguridad intencional para que Checkov lo detecte!
  # (El firewall debería estar cerrado)
}
