🔍 Étapes pour obtenir le PO Token et VISITOR_DATA :
1. Ouvrir YouTube sans être connecté

Ouvrez un navigateur en mode privé/incognito
Allez sur https://www.youtube.com/embed/aqz-KE-bpKQ (ou n'importe quelle vidéo YouTube embedded)
IMPORTANT : Assurez-vous de ne pas être connecté à un compte !

2. Ouvrir les outils développeur

Appuyez sur F12 pour ouvrir les outils développeur
Allez dans l'onglet "Network" (Réseau)
Dans le filtre, tapez v1/player pour filtrer les requêtes

3. Déclencher la requête

Cliquez sur la vidéo pour la lancer
Une requête player apparaîtra dans l'onglet Network

4. Extraire les données

Cliquez sur la requête player qui apparaît
Allez dans l'onglet "Payload" ou "Request"
Cherchez dans le JSON :

PO Token : serviceIntegrityDimensions.poToken
Visitor Data : context.client.visitorData



5. Mettre à jour votre fichier .env
Créez ou modifiez votre fichier .env :
envPO_TOKEN=votre_po_token_copié_ici
VISITOR_DATA=votre_visitor_data_copié_ici
🎯 Alternative plus simple pour tester :
Si vous voulez juste tester rapidement sans configurer le PO token, le code que j'ai modifié essaiera d'abord sans PO token, ce qui fonctionne souvent très bien !
🔧 Exemple de ce que vous devriez voir :
Dans le JSON de la requête, vous cherchez quelque chose comme :
json{
  "context": {
    "client": {
      "visitorData": "CgtVc0hKT2pHRnlHSSia..."
    }
  },
  "serviceIntegrityDimensions": {
    "poToken": "MnUxNWZlMmYtNzBkNy00..."
  }
}